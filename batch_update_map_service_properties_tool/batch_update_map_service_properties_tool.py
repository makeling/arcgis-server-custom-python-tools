#-*- coding: UTF-8 -*-
__author__ = 'keling ma'
# !/usr/bin/python

import requests
import os,json,sys
import time

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

    file_write_format(file, "conns:" + str(conns) )

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']
    else:
        return

    settings = get_config_params(server_config)

    file_write_format(file, "settins:" + str(settings) )

    if settings != None:
        services_list = settings['services_list']
        properties = settings['properties']
        folder = settings['folder']
        service_name_prefix = settings['service_name_prefix']

    else:
        return

    file_write_format(file, printSplitLine('generating token'))

    token = generate_token(url, username, password)

    file_write_format(file, "token" + token)

    file_write_format(file, printSplitLine('getting full service list'))

    file.close()

    service_count,full_services_list = get_services_list(export_file,url,token)

    loop_services(export_file, url, token, full_services_list, services_list, properties, folder, service_name_prefix)

# update service properties
def loop_services(export_file,url,token,full_services_list, services_list, properties,folder,service_name_prefix):
    file = open(export_file, 'a+')
    for service in full_services_list:
        service_name = service['serviceName']
        if len(services_list) != 0:
            for update_service_name in services_list:
                if service_name == update_service_name:
                    update_service_properties_by_folder(export_file,url, token, service, properties)
        else:
            if (service['folderName'] == folder or folder == "") and str(service_name).__contains__(service_name_prefix):
                update_service_properties_by_folder(export_file,url,token,service,properties)

    file_write_format(file,printSplitLine("update finished!"))
    file.close()



#update service instances by folder
def update_service_properties_by_folder(export_file, url, token,service,update_properties):
    try:
        file = open(export_file, 'a+')
        service_name = service['serviceName']

        file_write_format(file,printSplitLine('updating service: ' + str(service_name)))
        # file.write(printSplitLine('updating service: ' + str(service_name)))

        fullSvcName = service['serviceName'] + "." + service['type']
        folder = service['folderName']
        time0,properties = get_service_properties(export_file,url, token, folder, fullSvcName)

        for key in update_properties.keys():
            file_write_format(file, "update property:" + str(key) + "=" + str(properties[key]))
            properties[key] = update_properties[key]

        jsonProp = json.dumps(properties)
        time1,status = update_service_properties(url, token, folder, fullSvcName, jsonProp)

        file_write_format(file, "edit result:" + status['status'])
        t = str(float(time0[:-1]) + float(time1[:-1])) + "s"

        file_write_format(file, "response time: " + str(t))
        file.close()

    except:
        file_write_format(file, "update service properties failed!")
        file.close()
        return




# update service properties
def update_service_properties(url,token,folder,serviceName,properties):
    if folder != "/":
        service_url = url + "/admin/services/" + folder + "/" + serviceName + "/edit"
    else:
        service_url = url + "/admin/services/"  + serviceName + "/edit"
    # print("service_url:",service_url)
    params = {'token': token, 'f': 'json', 'service': properties}

    result = submit_request(service_url,params)
    return result

# get service properties
def get_service_properties(export_file,url,token,folder,serviceName):
    try:
        file = open(export_file, 'a+')
        if folder != "/":
            service_url = url + "/admin/services/" + folder + "/" + serviceName
        else:
            service_url = url + "/admin/services/" +  serviceName

        file_write_format(file, "service url:" + str(service_url))
        params = {'token': token, 'f': 'json'}
        result = submit_request(service_url,params)
        file.close()
        return result
    except:
        file.write("get service properties failed!")
        return

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

#format the export informations
def file_write_format(file,input_str):
    print(input_str)
    file.write(input_str + "\n")

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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))