#-*- coding: UTF-8 -*-
# !/usr/bin/python
__author__ = 'keling ma'

import os,json,sys
import time
import common_utils

# Defines the entry point into the script
def main(argv=None):
    print("let's start!")

    export_file = common_utils.generate_export_file()

    current_path = os.getcwd()
    server_config = current_path + os.sep + 'ags_pms.conf'

    url, username, password, services_list, folder, service_name_prefix=initialize_parameters(export_file,server_config)

    token = common_utils.generate_token(export_file,url, username, password)

    service_count, full_services_list,folders = common_utils.get_services_list(export_file, url, token)

    delete_services(export_file, url, token, full_services_list, services_list, folder, service_name_prefix)


# update service properties
def delete_services(export_file,url,token,full_services_list, services_list, folder,service_name_prefix):
    file = open(export_file, 'a+')
    common_utils.file_write_format(file, common_utils.printSplitLine("start delete service"))
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
    common_utils.file_write_format(file, common_utils.printSplitLine("task finished!"))
    file.close()

# delete single service operation
def delete_service(export_file,url, token, service):
    try:
        file = open(export_file, 'a+')
        service_name = service['serviceName']
        folder = service['folderName']

        if folder != "/":
            service_url = url + "/admin/services/" + folder + "/" + service_name + "." + service['type'] + "/delete"
        else:
            service_url = url + "/admin/services/"  + service_name + "."+service['type'] + "/delete"

        common_utils.file_write_format(file, "service_url:"+ str(service_url))

        params = {'token': token, 'f': 'json'}

        result = common_utils.submit_request(service_url,params)

        common_utils.file_write_format(file, "response time: " + str(result[0]))
        common_utils.file_write_format(file, "delete result:" + str(result[1]) + "\n")
        file.close()
    except:
        common_utils.file_write_format(file, "delete service"+ service_name+"failed!")
        file.close()
        return

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
        services_list = settings['services_list']
        folder = settings['folder']
        service_name_prefix = settings['service_name_prefix']

    file.close()
    return url,username,password,services_list,folder,service_name_prefix

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


