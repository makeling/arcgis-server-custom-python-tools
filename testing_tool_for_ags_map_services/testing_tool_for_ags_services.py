#-*- coding: UTF-8 -*-
__author__ = 'keling ma'
# !/usr/bin

import requests
import os,json,sys,getopt
import time
import random
import common_utils

# Defines the entry point into the script
def main(argv=None):
    print("let's start!")

    export_file = common_utils.generate_export_file()

    current_path = os.getcwd()
    server_config = current_path + os.sep + 'ags_pms.conf'

    url, username, password, interval, times = initialize_parameters(export_file, server_config)

    token = common_utils.generate_token(export_file, url, username, password)

    service_count, full_services_list, folders = common_utils.get_services_list(export_file, url, token)

    # begin test for request by interval and times
    request_services(export_file, url, token, service_count, full_services_list, interval, times)


# initialize parameters
def initialize_parameters(export_file,server_config):
    file = open(export_file,'a+')
    common_utils.file_write_format(file, "ags_pms.conf: " + str(server_config))
    file.write("\n")
    print("")

    conns = common_utils.get_server_conns_params(server_config)

    common_utils.file_write_format(file, "conns:" + str(conns))

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']


    settings = common_utils.get_config_params(server_config)

    common_utils.file_write_format(file, "settins:" + str(settings))

    if settings != None:
        interval = settings['interval']
        times = settings['request_times']

    file.close()
    return url,username,password,interval,times

#resquest servcies
def request_services(export_file,url,token,count,service_list,interval, times):
    file = open(export_file,'a+')
    common_utils.file_write_format(file, common_utils.printSplitLine("start testing"))
    response_str = ""
    total_time = 0.0
    mean_time = 0.0
    request_num = 0
    try:
        for i in range(times):
            s = random.randint(0, count - 1)
            service = service_list[s]
            common_utils.file_write_format(file, "selected service:" + str(service))

            if service['folderName'] == '/':
                service_url = url + "/rest/services/" + service['serviceName'] + "/" + service['type']
            else:
                service_url = url + "/rest/services/" + service['folderName'] + "/" +  service['serviceName'] + "/" + service['type']

            if service['type'] == 'MapServer':
                service_url += '/export'
                bbox = get_initialExtents(service_url,token)
                # print(bbox)
                if bbox == 'failed':
                    continue

                else:
                    random_bbox = generate_random_bbox(bbox)

                    common_utils.file_write_format(file, 'param_bbox:' + str(random_bbox))
                    params = get_export_map_parameters(token, random_bbox)
                    response = common_utils.submit_request(service_url, params)
                    elapse = str_conv_float(response[0])
                    total_time += elapse
                    request_num += 1

                    common_utils.file_write_format(file, 'response duration: ' + str(response[0]) + ' \n' + 'response content: '+str(response[1]))

            else:
                common_utils.file_write_format(file, "skip %s now!"%service['type'])

                common_utils.file_write_format(file, 'service url: ' + str(service_url) + '\n')
                time.sleep(interval)

            if int(request_num) == 0:
                mean_time = total_time
            else:
                mean_time = total_time / request_num
            common_utils.file_write_format(file,'\n')

        common_utils.file_write_format(file, common_utils.printSplitLine("Test task finished! "))

        common_utils.file_write_format(file, 'Total test services: ' + str(times))

        common_utils.file_write_format(file, 'All the requests consumed: ' + str("%.4f" % total_time) + 's')

        common_utils.file_write_format(file, 'Average response time: ' + str("%.4f" % mean_time) + 's')

    except:
        common_utils.file_write_format(file,"test failed!")

        file.close()

#assistant method for convert duration from string to float
def str_conv_float(elaple):
    l = len(elaple)

    return float(elaple[:l-1])

#assistant method for generate random bbox by initial Extent.
def generate_random_bbox(bbox):

    minx = bbox['xmin']
    miny = bbox['ymin']
    maxx = bbox['xmax']
    maxy = bbox['ymax']

    xmin = minx
    ymin = miny
    xmax = maxx
    maxy = maxy

    x1 = random.uniform(minx,maxx)
    x2 = random.uniform(minx,maxx)
    if x1 > x2:
        xmax = x1
        xmin = x2
    else:
        xmax = x2
        xmin = x1

    y1 = random.uniform(miny,maxy)
    y2 = random.uniform(miny,maxy)

    if y1 > y2:
        ymin = y2
        ymax = y1
    else:
        ymin = y1
        ymax = y2

    param_bbox = str(xmin)+","+str(ymin)+","+str(xmax)+","+str(ymax)

    return param_bbox

#assistant method for generate mapserver export parameters
def get_export_map_parameters(token,bbox):

    params = {'token': token, 'f': 'json','format':'png','transparent':False,'bbox':bbox}

    return params

# request get initial extents
def get_initialExtents(url,token):
    l = len(url)
    service_url = url[:l-7]
    print(service_url)

    params = {'token': token, 'f': 'json'}

    item = 'initialExtent'

    result = common_utils.submit_request(service_url,params,item)

    return result[1]

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))