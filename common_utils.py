#-*- coding: UTF-8 -*-
#!/usr/bin/python
#__author__ = 'keling ma'

import requests
import os,json,sys
import time


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

# generate token by arcgis server
def generate_token(url, username, password):
    try:
        tokenUrl = url + '/admin/generateToken'
        print("token url:", tokenUrl)
        # , 'ip':'192.168.100.85'
        params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}

        item = 'token'

        r = submit_request(tokenUrl, params, item)

        return r[1]
    except:
        print("get token failed, please check url, username, password.")
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
        return err_flag

# assert response json
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print('Error: JSON object returns an error.' + str(obj))
        sys.exit(False)
    else:
        return True


