#-*- coding: UTF-8 -*-
__author__ = 'keling ma'
# !/usr/bin

import requests
import os,json,sys,getopt
import time
import random

# Defines the entry point into the script
def main(argv=None):
    print("let's start!")
    print(printSplitLine('creating export result file'))
    current_path = os.getcwd()
    export_file = create_result_file(current_path)
    file = open(export_file, 'a+')

    file_write_format(file, "export_file: " + str(export_file))

    file_write_format(file, printSplitLine('initializing parameters'))

    server_config = current_path + os.sep + 'ags_pms.conf'

    file_write_format(file, "ags_pms.conf: " + str(server_config))
    file.write("\n")
    print("")

    conns = get_server_conns_params(server_config)

    file_write_format(file, "conns:" + str(conns))

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']
    else:
        return

    settings = get_config_params(server_config)

    file_write_format(file, "settins:" + str(settings))

    if settings != None:
        interval = settings['interval']
        times = settings['request_times']
        loop = settings['loop']

    else:
        return

    file_write_format(file, printSplitLine('generating token'))

    token = generate_token(url, username, password)

    file_write_format(file, "token" + token)

    file.close()

    service_count, full_services_list = get_services_list(export_file, url, token)

    # begin test for request by interval and times
    request_services(export_file, url, token, service_count, full_services_list, interval, times)


# print a dash line for format the different part.
def printSplitLine(comment):
    splitline = ""
    count = 0
    for i in range(50):
        splitline += "-"
        count +=1
        if count == 25:
            splitline += comment


    return (splitline + "\n")

#resquest servcies
def request_services(export_file,url,token,count,service_list,interval, times):
    file = open(export_file,'a+')
    file_write_format(file, printSplitLine("start testing"))
    response_str = ""
    total_time = 0.0
    mean_time = 0.0
    request_num = 0
    try:
        for i in range(times):
            s = random.randint(0, count - 1)
            service = service_list[s]
            file_write_format(file, "selected service:" + str(service))

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

                    file_write_format(file, 'param_bbox:' + str(random_bbox))
                    params = get_export_map_parameters(token, random_bbox)
                    response = submit_request(service_url, params)
                    elapse = str_conv_float(response[0])
                    total_time += elapse
                    request_num += 1

                    file_write_format(file, 'response duration: ' + str(response[0]) + ' \n' + 'response content: '+str(response[1]))

            else:
                file_write_format(file, "skip %s now!"%service['type'])

                file_write_format(file, 'service url: ' + str(service_url) + '\n')
                time.sleep(interval)

            if int(request_num) == 0:
                mean_time = total_time
            else:
                mean_time = total_time / request_num
            file_write_format(file,'\n')

        file_write_format(file, printSplitLine("successfully complete all the test!"))

        file_write_format(file, 'Total test services: ' + str(times))

        file_write_format(file, 'All the requests consumed: ' + str("%.4f" % total_time) + 's')

        file_write_format(file, 'Average response time: ' + str("%.4f" % mean_time) + 's')

    except:
        file_write_format(file,"test failed!")

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

#format the export informations
def file_write_format(file,input_str):
    print(input_str)
    file.write(input_str + "\n")

# method for get the connection parameters from a json file
def get_server_conns_params(config_file):
    try:
        file = open(config_file)
        params = json.load(file)
        # print(params)
        conns = params['conns']
        # print(conns)
        file.close()
        return conns
    except:
        print("open ags_pms.conf file failed, please check the path.")
        return

# method for get the config parameters from a json file
def get_config_params(config_file):
    try:
        file = open(config_file)
        params = json.load(file)
        # print(params)
        settings = params['settings']
        # print(settings)
        file.close()
        return settings
    except:
        print("open ags_pms.conf file failed, please check the path.")
        return

#assistant method for submit request
def submit_request(url,params,item=""):
    err_flag = 'failed'
    try:
        r = requests.post(url, data=params, verify=False)

        if (r.status_code != 200):
            r.raise_for_status()
            print('request failed.')
            return err_flag
        else:
            data = r.text
            elapse_time = str(r.elapsed.microseconds/1000/1000) + 's'
            # Check that data returned is not an error object
            if not assertJsonSuccess(data):
                return
            # Extract service list from data
            result = json.loads(data)

            if item != "":
                last_result = result[item]
            else:
                last_result = result
            return elapse_time,last_result
    except :
        print("request failed")
        return err_flag

# assert response json
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print('Error: JSON object returns an error.' + str(obj))
        sys.exit(False)
    else:
        return True

# request get initial extents
def get_initialExtents(url,token):
    l = len(url)
    service_url = url[:l-7]
    print(service_url)

    params = {'token': token, 'f': 'json'}

    item = 'initialExtent'

    result = submit_request(service_url,params,item)

    return result[1]

# get folder list and services list in every folder.
def get_services_list(export_file, url, token):
    try:
        file = open(export_file, 'a+')

        request_url = url + "/admin/services"
        folders = ['/']
        params = {'token': token, 'f': 'json'}
        item = 'folders'
        result = submit_request(request_url, params, item)

        if result != "failed":
            for f in result[1]:
                if str.upper(f) == "SYSTEM" or str.upper(f) == "UTILITIES" or str.upper(f) == "HOSTED":
                    continue
                else:
                    folders.append(f)

        file_write_format(file, "All the folders:" + str(folders))

        services_list = []
        if folders != None:
            for folder in folders:
                if folder == '/':
                    folder_url = request_url
                else:
                    folder_url = request_url + "/" + folder
                item = 'services'
                services = submit_request(folder_url, params, item)
                for i in services[1]:
                    # file_write_format(export_file, str(i))
                    services_list.append(i)
        count = len(services_list)

        file_write_format(file, "services_count:" + str(count))
        file.write("\n")

        file.close()
        return count, services_list
    except:
        file_write_format(file, "get services list failed!")
        file.close()
        return

# get token by arcgis server
def generate_token(url, username, password):
    tokenUrl = url + '/admin/generateToken'
    print(tokenUrl)
    # , 'ip':'192.168.100.85'
    params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}

    item = 'token'

    r = submit_request(tokenUrl,params,item)

    return r[1]


# create a new dir in the current path for store the check result file.
def create_result_file(current_path):
    try:
        export_result_folder = current_path + os.sep + "check_results"
        if os.path.exists(export_result_folder) == False:
            os.mkdir(export_result_folder)
        timeStamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

        export_file = export_result_folder + os.sep + "result_" + timeStamp + ".txt"

        file = open(export_file, 'w')

        time_log = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        file.write("\n")
        file_write_format(file, "update time：" + time_log)
        file.write("\n")

        file.close()
        # export_result_name = service_status

        return export_file
    except:
        print("create the check_results folder or result file failed!")
        return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))