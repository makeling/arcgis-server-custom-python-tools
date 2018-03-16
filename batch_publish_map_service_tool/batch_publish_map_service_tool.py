#-*- coding: UTF-8 -*-
#!/usr/bin/python
#__author__ = 'keling ma'

import sys
import json
import requests
import os
import getopt
import common_utils

def main(argv=None):
    print("let's start!")

    export_file = common_utils.generate_export_file()

    current_path = os.getcwd()
    server_config = current_path + os.sep + 'ags_pms.conf'

    current_path = os.getcwd()
    service_config_file = current_path + os.sep + 'service.json'

    url, username, password, folder, start_num, service_count, service_name_prefix = initialize_parameters(export_file,
                                                                                                server_config)

    token = common_utils.generate_token(export_file, url, username, password)

    current_service_count, full_services_list, folders = common_utils.get_services_list(export_file, url, token)

    create_new_folder(export_file, url, token, folder,folders)

    publish_map_services(export_file,url,token,service_config_file,folder,service_name_prefix,start_num,service_count)



# create a new folder for arcgis server
def create_new_folder(export_file,url,token,folder,folders):
    try:
        file = open(export_file,'a+')
        exist = False
        for f in folders:
            if f == folder:
                common_utils.file_write_format(file, f + " folder exist")
                exist = True
                return
        if exist:
            common_utils.file_write_format(file, common_utils.printSplitLine("creating new folder"))
            create_folder_url =  url + "/admin/services/createFolder"
            params = {'folderName': folder,'description':folder,'f':'json','token':token}

            common_utils.file_write_format(file, common_utils.printSplitLine("create new folder : " + folder))
            common_utils.file_write_format(file, "request url:"+ create_folder_url)

            response = common_utils.submit_request(create_folder_url, params)
            common_utils.file_write_format(file, "response result: " + response)
            file.close()
    except:
        print("create new folder failed!")
        common_utils.file_write_format(file,"create new folder failed!")
        file.close()
        return

# initialize parameters
def initialize_parameters(export_file,server_config):
    file = open(export_file, 'a+')
    common_utils.file_write_format(file, "ags_pms.conf: " + str(server_config))
    file.write("\n")
    print("")

    conns = common_utils.get_server_conns_params(server_config)

    common_utils.file_write_format(file, "conns:" + str(conns))

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']


    # settings = common_utils.get_config_params(server_config)
    settings = common_utils.get_config_params(server_config)

    if settings != None:
        folder = settings['folder']
        start_num = settings['start_num']
        service_count = settings['service_count']
        service_name_prefix = settings['service_name_prefix']

    common_utils.file_write_format(file, "settings:" + str(settings))


    file.close()
    return url, username, password, folder,start_num, service_count, service_name_prefix

# batch publish and start map service
def publish_map_services(export_file,url,token,config_file,folder,service_name_prefix,start_num,service_count):
    file = open(export_file, "a+")
    if folder == "/":
        service_url = url + "/admin/services/"
    else:
        service_url = url + "/admin/services/" + folder + "/"

    create_service_url = service_url + "createService"


    try:
        for i in range(service_count):
            service_name = service_name_prefix + str(start_num+i)
            service_params = set_params(config_file,"serviceName",service_name)
            params = {'service': service_params,'f':'json','token':token}
            common_utils.file_write_format(file, common_utils.printSplitLine("publish and start map service : "+service_name))
            common_utils.file_write_format(file, "publishing service ...")
            common_utils.file_write_format(file,"request url:" + create_service_url)

            response = common_utils.submit_request(create_service_url, params)
            common_utils.file_write_format(file, "response time: " + str(response[0]))
            common_utils.file_write_format(file, "response result: " + str(response[1]))

            if response != None:
                common_utils.file_write_format(file, "starting service ...")
                start_service_url = service_url + service_name + ".MapServer/start"
                common_utils.file_write_format(file, "request url:" + start_service_url)
                params1 = {'token': token, 'f': 'json'}
                response = common_utils.submit_request(start_service_url,params1)
                common_utils.file_write_format(file, "response time: " + str(response[0]))
                common_utils.file_write_format(file, "response result: " + str(response[1]))

        common_utils.file_write_format(file, common_utils.printSplitLine("task finished!"))
        file.close()
    except:
        common_utils.file_write_format(file, "publishing service failed!")
        file.close()
        return


# load services config file and reset service name params dictionary
def set_params(config_file,key,value):
    try:
        file = open(config_file)
        params = json.load(file)
        for k in params.keys():
            if k == key:
                params[k] = value
        file.close()
        return json.dumps(params)
    except:
        print("open ags_pms.conf file failed, please check the path.")
        return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
