#-*- coding: UTF-8 -*-
__author__ = 'keling ma'
# !/usr/bin/python

import requests
import os,json,sys
import time
import common_utils

# Defines the entry point into the script
def main(argv=None):
    print("let's start!")

    export_file = common_utils.generate_export_file()

    current_path = os.getcwd()
    server_config = current_path + os.sep + 'ags_pms.conf'

    url, username, password, services_list, properties, folder, service_name_prefix = initialize_parameters(export_file,
                                                                                                server_config)
    token = common_utils.generate_token(export_file, url, username, password)

    service_count, full_services_list, folders = common_utils.get_services_list(export_file, url, token)

    loop_services(export_file, url, token, full_services_list, services_list, properties, folder, service_name_prefix)

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
        properties = settings['properties']
        folder = settings['folder']
        service_name_prefix = settings['service_name_prefix']

    file.close()
    return url,username,password,services_list,properties,folder,service_name_prefix

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

    common_utils.file_write_format(file, common_utils.printSplitLine("update finished!"))
    file.close()

#update service instances by folder
def update_service_properties_by_folder(export_file, url, token,service,update_properties):
    try:
        file = open(export_file, 'a+')
        service_name = service['serviceName']

        common_utils.file_write_format(file, common_utils.printSplitLine('updating service: ' + str(service_name)))
        # file.write(printSplitLine('updating service: ' + str(service_name)))

        fullSvcName = service['serviceName'] + "." + service['type']
        folder = service['folderName']
        time0,properties = get_service_properties(export_file,url, token, folder, fullSvcName)

        for key in update_properties.keys():
            common_utils.file_write_format(file, "update property:" + str(key) + "=" + str(properties[key]))
            properties[key] = update_properties[key]

        jsonProp = json.dumps(properties)
        time1,status = update_service_properties(url, token, folder, fullSvcName, jsonProp)

        common_utils.file_write_format(file, "edit result:" + status['status'])
        t = str(float(time0[:-1]) + float(time1[:-1])) + "s"

        common_utils.file_write_format(file, "response time: " + str(t))
        file.close()

    except:
        common_utils.file_write_format(file, "update service properties failed!")
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

    result = common_utils.submit_request(service_url,params)
    return result

# get service properties
def get_service_properties(export_file,url,token,folder,serviceName):
    try:
        file = open(export_file, 'a+')
        if folder != "/":
            service_url = url + "/admin/services/" + folder + "/" + serviceName
        else:
            service_url = url + "/admin/services/" +  serviceName

        # common_utils.file_write_format(file, "service url:" + str(service_url))
        params = {'token': token, 'f': 'json'}
        result = common_utils.submit_request(service_url,params)
        file.close()
        return result
    except:
        file.write("get service properties failed!")
        return




if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))