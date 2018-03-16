#-*- coding: UTF-8 -*-
#!/usr/bin/python
#__author__ = 'keling ma'

import requests
import os,json,sys
import time
import collections


# get folder list and services list in every folder.
def get_services_list(export_file, url, token):
    try:
        file = open(export_file, 'a+')

        file_write_format(file, printSplitLine('getting full service list'))

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
                    services_list.append(i)
        count = len(services_list)

        file_write_format(file, "services_count:" + str(count))
        file.write("\n")

        file.close()
        return count, services_list,folders
    except:
        file_write_format(file, "get services list failed!")
        file.close()
        return

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

# print a dash line for format the different printing part.
def printSplitLine(comment):
    splitline = ""
    count = 0
    for i in range(50):
        splitline += "-"
        count += 1
        if count == 25:
            splitline += comment

    return "\n" + splitline + "\n"


#format the export informations
def file_write_format(file,input_str):
    print(input_str)

    try:
        if isinstance(getattr(file, "read"), collections.Callable) \
                and isinstance(getattr(file, "close"), collections.Callable):
            file.write(input_str + "\n")
    except AttributeError:
        pass


# generate token by arcgis server
def generate_token(export_file,url, username, password):
    try:
        file = open(export_file, 'a+')

        file_write_format(file, printSplitLine('generating token'))

        tokenUrl = url + '/admin/generateToken'
        print("token url:", tokenUrl)
        # , 'ip':'192.168.100.85'
        params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}

        item = 'token'

        r = submit_request(tokenUrl, params, item)

        file_write_format(file, "token" + r[1])

        file.close()

        return r[1]
    except:
        print("get token failed, please check url, username, password.")
        file.close()
        return

# assistant method for submit request
def submit_request(url, params, item=""):
    err_flag = 'failed'
    try:
        r = requests.post(url, data=params, verify=False)

        if (r.status_code != 200):
            r.raise_for_status()
            print('request failed.')
            return err_flag
        else:
            data = r.text
            elapse_time = str(r.elapsed.microseconds / 1000 / 1000) + 's'
            # Check that data returned is not an error object
            if not assertJsonSuccess(data):
                return
            # Extract service list from data
            result = json.loads(data)

            if item != "":
                last_result = result[item]
            else:
                last_result = result
            return elapse_time, last_result
    except:
        print("request failed")
        return elapse_time,err_flag


# assert response json
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print('Error: JSON object returns an error.' + str(obj))
        sys.exit(False)
    else:
        return True


def generate_export_file():

    print(printSplitLine('creating export result file'))
    current_path = os.getcwd()
    export_file = create_result_file(current_path)
    print(export_file)
    file = open(export_file, 'a+')

    file_write_format(file, "export_file: " + str(export_file))

    file.close()


    return export_file

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

