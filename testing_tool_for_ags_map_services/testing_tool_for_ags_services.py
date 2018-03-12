#-*- coding: UTF-8 -*-
__author__ = 'keling ma'
# !/usr/bin

import requests
import os,json,sys,getopt
import time
import random

# Defines the entry point into the script
def main(argv=None):
    # Ask for admin/publisher user name and password
    opts, args = getopt.getopt(argv,"u:p:a:i:t:l:")
    username = ""
    password = ""
    url = ""
    interval = 1
    times = 1
    loop = False
    if len(opts) == 0:
        print("please input parameters eg: -u siteadmin -p Super123 -a https://office.esrichina.com:6443/arcgis -i 3 -t 10 -l False")
        print('-u : The username of arcgis server site administrator')
        print('-p : The password of arcgis server site administrator')
        print('-a : The url of testing arcgis server site')
        print('-i : The interval of requests, unit - (s)')
        print('-t: The request times')
        print('-l: Whether loop all the subfolders in the arcgis server site, the default value is False!')
        print('Good Luck!')
        return

    for op, value in opts:
        print("op:",op,"value: ",value)
        if op == "-u":
            username = value
        elif op == "-p":
            password = value
        elif op == "-a":
            url = value
        elif op == "-i":
            interval = int(value)
        elif op == "-t":
            times = int(value)
        elif op == "-l":
            loop = value


    current_path = os.getcwd()
    # current_path = '/Users/maklmac/Desktop'
    # i
    time_stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    file_path = current_path + os.path.sep + "test_" + str(time_stamp) + '.txt'
    print(file_path)
    file = open(file_path, 'w')
    try:
        #1 print user input parameters
        file.write(printSplitLine('input parameters: '))
        file.write('\n')
        print(printSplitLine('input parameters: '))
        print('username: ', username, 'password: ', password, 'url: ', url, 'interval: ', interval, 'times: ', times,
              'loop:  ', loop)
        file.write('username: ' + username +
                   ', password: ' + password + ', url:' + url + ', interval:' + str(interval) + ', times:' + str(
                       times) + ', loop:' + str(loop) + '\n')
        file.write('\n')

        # username = "siteadmin"
        # password = "Super123"
        # server_url = r"https://office.esrichina.com:6443/arcgis"
        #2 get token
        print(printSplitLine("getting token..."))
        file.write('\n')
        file.write(printSplitLine("getting token..."))
        # get token
        token = generateToken(url, username, password)
        print("token:", token)
        file.write("token:"+ token + '\n')
        file.write('\n')

        # 3 get services list
        file.write(printSplitLine("getting service list..."))
        file.write('\n')
        print(printSplitLine("getting service list..."))

        service_list = []

        count, result = getServiceList(url, token, loop)

        if result != "failed":
            service_list = result

        print("services count:", count)

        file.write("services count:" + str(count) + '\n')
        i = 1
        for service in service_list:
            print("service%s:" % i, service)
            file.write("service")
            file.write(str(i))
            file.write(": ")
            file.write(str(service))
            file.write('\n')
            i += 1

        file.write('\n')

        # 4 start testing
        file.write(printSplitLine("start testing..."))
        file.write('\n')
        print(printSplitLine("start testing..."))
        # begin test for request by interval and times
        response = request_services(url, token, count, service_list, interval, times)

        file.write(str(response[2]) + '\n')

        #5 print response time
        file.write(printSplitLine("computing response time..."))
        file.write('\n')

        print(printSplitLine("computing response time..."))

        file.write('All the requests consumed: '+str("%.4f" % response[0]) + 's'+'\n')

        print('All the requests consumed:'+str("%.4f" % response[0])+ 's' + '\n')

        file.write('Average response time: ' + str("%.4f" % response[1]) + 's' + '\n')

        print('Average response time:' + str("%.4f" % response[1])+ 's' + '\n')
        file.write('\n')

        # 6 the end
        file.write(printSplitLine("successfully complete all the test!") + '\n')

        print(printSplitLine("successfully complete all the test!"))

        file.close()

    except:
        file.close()
        return

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
def request_services(url,token,count,serviceList,interval, times):
    response_str = ""
    total_time = 0.0
    mean_time = 0.0
    request_num = 0
    for i in range(times):
        s = random.randint(0, count-1)
        service = serviceList[s]
        print("selected service:" , service)
        # file.write("selected service:" + str(service) + '\n')
        response_str += "selected service:" + str(service) + '\n'
        service_url = url

        service_url += "/rest/services" + "/" + service['name'] + "/" + service['type']

        if service['type'] == 'MapServer':
            service_url += '/export'
            bbox = get_initialExtents(service_url,token)
            # print(bbox)
            if bbox == 'failed':
                continue

            else:
                random_bbox = generate_random_bbox(bbox)
                response_str += 'param_bbox:' + str(random_bbox) + '\n'
                params = get_export_map_parameters(token, random_bbox)
                response = submit_request(service_url, params)
                elapse = str_conv_float(response[0])
                total_time += elapse
                request_num += 1
                response_str += 'response duration: ' + str(response[0]) + ' \n' + 'response content: '+str(response[1]) + '\n'
                print('response duration: ' + str(response[0]) + ' \n' + 'response content: '+str(response[1]))
        else:
            print("skip %s now!"%service['type'])
            response_str += 'skip ' + str(service['type']) + 'now!' + '\n'

        print("service url: ",service_url,'\n')
        response_str += 'service url: ' + str(service_url) + '\n' + '\n'
        time.sleep(interval)

    if int(request_num) == 0:
        mean_time = total_time
    else:
        mean_time = total_time / request_num

    return total_time,mean_time,response_str

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

# get foldeer and services list in folder
def getServiceList(url,token,loop_sub_folder="False"):
    url += '/rest/services'
    folders = ['/']
    params = {'token': token, 'f': 'json'}

    if str.upper(loop_sub_folder)== "TRUE":
        item = 'folders'
        result = submit_request(url, params, item)
        if result != "failed":
            for f in result[1]:
                if str.upper(f) == "SYSTEM" or str.upper(f) == "UTILITIES" or str.upper(f) == "HOSTED":
                    continue
                else:
                    folders.append(f)

    print("All the folders:",folders)


    services_list = []
    if folders != None:
        for folder in folders:
            if folder == '/':
                folder_url = url
            else:
                folder_url = url + "/" + folder
            item = 'services'
            services = submit_request(folder_url, params,item)
            for i in services[1]:
                services_list.append(i)
    count = len(services_list)

    return count,services_list

# get token by arcgis server
def generateToken(url, username, password):
    tokenUrl = url + '/admin/generateToken'
    print(tokenUrl)
    # , 'ip':'192.168.100.85'
    params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}

    item = 'token'

    r = submit_request(tokenUrl,params,item)

    return r[1]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))