#-*- coding: UTF-8 -*-
# !/usr/bin/python
__author__ = 'keling ma'

import os,json,sys
import time
import common_utils

# Defines the entry point into the script
def main(argv=None):
    print("let's start!")

    export_file = generate_export_file()

    current_path = os.getcwd()
    server_config = current_path + os.sep + 'ags_pms.conf'

    url, username, password, services_list, folder, service_name_prefix=initialize_parameters(export_file,server_config)

    print(url, username, password, services_list, folder, service_name_prefix)

    file = open(export_file,'a+')

    file_write_format(file, common_utils.printSplitLine('generating token'))

    token = common_utils.generate_token(url, username, password)

    file_write_format(file, "token" + token)

    file_write_format(file, common_utils.printSplitLine('getting full service list'))

    file.close()

    service_count, full_services_list = get_services_list(export_file, url, token)

    delete_services(export_file, url, token, full_services_list, services_list, folder, service_name_prefix)


# update service properties
def delete_services(export_file,url,token,full_services_list, services_list, folder,service_name_prefix):
    file = open(export_file, 'a+')
    file_write_format(file, common_utils.printSplitLine("start delete service"))
    file.close()
    for service in full_services_list:
        service_name = service['serviceName']
        if len(services_list) != 0:
            for delete_service_name in services_list:
                if service_name == delete_service_name:
                    delete_service(export_file,url, token, service)

        else:
            if (service['folderName'] == folder or folder == "") and str(service_name).__contains__(service_name_prefix):
                delete_service(export_file,url,token, service)

    file = open(export_file, 'a+')
    file_write_format(file, common_utils.printSplitLine("task finished!"))
    file.close()


def delete_service(export_file,url, token, service):
    try:
        file = open(export_file, 'a+')
        service_name = service['serviceName']
        folder = service['folderName']

        if folder != "/":
            service_url = url + "/admin/services/" + folder + "/" + service_name + "." + service['type'] + "/delete"
        else:
            service_url = url + "/admin/services/"  + service_name + "."+service['type'] + "/delete"

        file_write_format(file, "service_url:"+ str(service_url))

        params = {'token': token, 'f': 'json'}

        result = common_utils.submit_request(service_url,params)

        file_write_format(file, "response time: " + str(result[0]))
        file_write_format(file, "delete result:" + str(result[1]) + "\n")
        file.close()
    except:
        file_write_format(file, "delete service"+ service_name+"failed!")
        file.close()
        return

# get folder list and services list in every folder.
def get_services_list(export_file, url, token):
    try:
        file = open(export_file, 'a+')

        request_url = url + "/admin/services"
        folders = ['/']
        params = {'token': token, 'f': 'json'}
        item = 'folders'
        result = common_utils.submit_request(request_url, params, item)

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
                services = common_utils.submit_request(folder_url, params, item)
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

def generate_export_file():

    print(common_utils.printSplitLine('creating export result file'))
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

def initialize_parameters(export_file,server_config):
    file = open(export_file,'a+')
    file_write_format(file, "ags_pms.conf: " + str(server_config))
    file.write("\n")
    print("")

    conns = common_utils.get_server_conns_params(server_config)

    file_write_format(file, "conns:" + str(conns))

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']


    settings = common_utils.get_config_params(server_config)

    file_write_format(file, "settins:" + str(settings))

    if settings != None:
        services_list = settings['services_list']
        folder = settings['folder']
        service_name_prefix = settings['service_name_prefix']

    file.close()
    return url,username,password,services_list,folder,service_name_prefix


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


#format the export informations
def file_write_format(file,input_str):
    print(input_str)
    file.write(input_str + "\n")

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


