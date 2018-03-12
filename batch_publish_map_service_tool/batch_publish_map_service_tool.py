#-*- coding: UTF-8 -*-
#!/usr/bin/python
#__author__ = 'keling ma'

import sys
import json
import requests
import os
import getopt

def main(argv=None):
    # Ask for admin/publisher user name and password
    opts, args = getopt.getopt(argv, "s:a:")
    config_file = ""
    server_config = ""
    if len(opts) == 0:
        print(
            "Please input service.json path and ags_pms.config path, eg: -s 'c:\\\\Users\\maklmac\\Desktop\\service.json' -a 'c:\\\\Users\\maklmac\\Desktop\\ags_pms.conf' . "
            )
        print("If you don't set , the default value would use the same path with the python script exist. ")
        print('-s : The path of service.json(optional)')
        print('-a : The path of ags_pms.conf(optional)')

        print("")
        print("let's start!")


    for op, value in opts:
        print("op:", op, "value: ", value)
        if op == "-s":
            config_file = value
        elif op == "-a":
            server_config = value

    current_path = os.getcwd()

    if config_file == "":
        config_file = current_path + os.sep + 'service.json'
        print("config_file", config_file)

    if server_config == "":
        server_config = current_path + os.sep + 'ags_pms.conf'
        print("server_config",server_config)

    print("")

    # config_file = "/Users/maklmac/Desktop/service.json"
    # server_config = "/Users/maklmac/Desktop/ags_pms.conf"

    conns = get_server_conns_params(server_config)

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']
    else:
        return

    settings = get_publish_params(server_config)

    if settings != None:
        folder = settings['folder']
        start_num = settings['start_num']
        service_count = settings['service_count']
        service_name_prefix = settings['service_name_prefix']
    else:
        return

    try:
        token = generateToken(url,username,password)

    except:
        print("get token failed, please check url, username, password.")
        return

    if folder != "/":
        create_new_folder(url,token,folder)

    publish_map_services(url,token,config_file,folder,service_name_prefix,start_num,service_count)


def create_new_folder(url,token,folder):
    try:
        create_folder_url =  url + "/admin/services/createFolder"
        params = {'folderName': folder,'description':folder,'f':'json','token':token}

        printSplitLine("create new folder : " + folder)
        print("creating new folder ...")
        print("request url:", create_folder_url)
        response = submit_request(create_folder_url, params)
        print("response result: ", response)
    except:
        print("create new folder failed!")
        return


# batch publish and start map service
def publish_map_services(url,token,config_file,folder,service_name_prefix,start_num,service_count):
    if folder == "/":
        service_url = url + "/admin/services/"
    else:
        service_url = url + "/admin/services/" + folder + "/"

    create_service_url = service_url + "createService"

    try:
        for i in range(service_count):
            service_name = service_name_prefix + str(start_num+i)
            service_params = set_params(config_file,"serviceName",service_name)
            # print(service_params)
            # params = {'token': token, 'f': 'json','service': service_params}
            params = {'service': service_params,'f':'json','token':token}
            printSplitLine("publish and start map service : "+service_name)
            print("publishing service ...")
            print("request url:", service_url)
            response = submit_request(create_service_url, params)
            print("response result: ",response)

            if response != 'failed':
                print("starting service ...")
                start_service_url = service_url + service_name +".MapServer/start"
                print("request url:",start_service_url)
                params1 = {'token': token, 'f': 'json'}
                response = submit_request(start_service_url,params1)
                print("response result: ", response)
    except:
        print("publishing service failed!")
        return

def get_publish_params(config_file):
    try:
        file = open(config_file)
        params = json.load(file)
        settings = params['settings']
        print(settings)
        file.close()
        return settings
    except:
        print("open service.json file failed, please check the path.")
        return



# get config params from json
def get_server_conns_params(config_file):
    try:
        file = open(config_file)
        params = json.load(file)
        # print(params)
        conns = params['conns']
        print(conns)
        file.close()
        return conns
    except:
        print("open service.json file failed, please check the path.")
        return

# load config file and return params dictionary
def set_params(config_file,key,value):
    try:
        file = open(config_file)
        params = json.load(file)
        # print(params)
        for k in params.keys():
            if k == key:
                # print(key)
                params[k] = value
                # print(params[k])
        # print(params)
        file.close()
        return json.dumps(params)
    except:
        print("open ags_pms.conf file failed, please check the path.")
        return

# print a dash line for format the different part.
def printSplitLine(comment):
    print("")
    splitline = ""
    count = 0
    for i in range(50):
        splitline += "-"
        count +=1
        if count == 25:
            splitline += comment

    print(splitline + "\n")

# get token by arcgis server
def generateToken(url, username, password):
    tokenUrl = url + '/admin/generateToken'
    # print(tokenUrl)
    # , 'ip':'192.168.100.85'
    params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}
    item = 'token'
    r = submit_request(tokenUrl,params,item)
    return r[1]


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

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
