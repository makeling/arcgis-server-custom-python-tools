#-*- coding: UTF-8 -*-
#!/usr/bin/python
#__author__ = 'keling ma'


import json
import requests
import os,sys,time
import common_utils

def main(argv=None):
    print("let's start!")

    export_file = common_utils.generate_export_file()

    current_path = os.getcwd()
    server_config = current_path + os.sep + 'ags_pms.conf'

    url, username, password, repair_times = initialize_parameters(export_file,server_config)

    token = common_utils.generate_token(export_file, url, username, password)

    service_count, full_services_list, folders = common_utils.get_services_list(export_file, url, token)

    check_service_status(export_file,url,token,full_services_list,int(repair_times))

    check_instance_statistics(export_file,url,token,full_services_list,int(repair_times))


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
        repair_times = settings['repair_times']

    file.close()
    return url,username,password,repair_times


#check service instance status, then return error list and try to repair by restart service.
def check_instance_statistics(export_file,url,token,service_list,repair_times):
    try:
        file = open(export_file, 'a+')

        error_log = "位于{0}目录下的服务{1}在服务器{2}创建实例异常: 应创建最小实例数：{3}, 实际创建实例数：{4}。\n服务地址：{5} \n"

        error_services = {}

        common_utils.file_write_format(file, common_utils.printSplitLine("start checking instance statistics"))


        for service in service_list:
            folder = service['folderName']
            serviceName = service['serviceName']
            type = service['type']

            if folder == "/":
                base_url = url + "/admin/services/"
            else:
                base_url = url + "/admin/services/" + folder + "/"

            params = {'token': token, 'f': 'json'}

            service_url = base_url + serviceName + "." + type

            common_utils.file_write_format(file, "checking service: " + service_url)

            responsetime, service_detail = common_utils.submit_request(service_url,params)

            # print(service_detail)

            min_instance_config = service_detail['minInstancesPerNode']

            stat_url = service_url + "/statistics"

            response = common_utils.submit_request(stat_url, params)

            statistics = response[1]
            summary = statistics['summary']
            machines = statistics['perMachine']
            m_count = len(machines)

            for machine in machines:
                machineName = machine['machineName']
                if machine['isStatisticsAvailable']:
                    # print(machine)
                    running_ins = int(machine['free']) + int(machine['busy'])

                    if running_ins < min_instance_config:
                        common_utils.file_write_format(file, error_log.format(folder, serviceName, machineName, min_instance_config, running_ins,
                                               service_url) + "\n")


                        error_services[serviceName] = service_url
                    else:
                        common_utils.file_write_format(file, "check " + machineName +" result : normal" )

        file.close()

        if len(error_services.keys()) > 0 :
            file = open(export_file, "a+")
            common_utils.file_write_format(file, common_utils.printSplitLine("check finished，continue to repair the instances"))

            for service in error_services.keys():
                serviceName = service
                service_url = error_services[service]
                common_utils.file_write_format(file, "repairing service :" + service_url)

                result = repair_bugs(repair_times,serviceName,service_url,token)

                common_utils.file_write_format(file, "repair result :" + str(result))

            common_utils.file_write_format("repair instance status finished!")

            file.close()

        file = open(export_file, "a+")

        common_utils.file_write_format(file, common_utils.printSplitLine("check finished!"))

        file.close()


    except:
        common_utils.file_write_format(file, "check instanse failed!")
        file.close()
        return

#check service status, then export the status list and try to repair the bug.
def check_service_status(export_file,url,token,service_list,repair_times):
    try:
        error_log = "位于{0}目录下的服务{1}启动异常: 配置状态：{2}, 实际状态：{3}。\n服务地址：{4} \n"

        file = open(export_file, 'a+')

        common_utils.file_write_format(file, common_utils.printSplitLine('start checking service status'))

        i = 0

        for service in service_list:
            folder = service['folderName']
            serviceName = service['serviceName']
            type = service['type']

            if folder == "/":
                base_url = url + "/admin/services/"
            else:
                base_url = url + "/admin/services/" + folder + "/"

            service_url = base_url + serviceName + "." + type

            common_utils.file_write_format(file, "checking service :" + service_url)

            check_url = service_url + "/status"

            params = {'token': token, 'f': 'json'}

            response = common_utils.submit_request(check_url,params)

            status = response[1]

            configuredState = status['configuredState']
            realTimeState = status['realTimeState']

            if configuredState != realTimeState:
                common_utils.file_write_format(file, error_log.format(folder, serviceName, configuredState, realTimeState, service_url))
                common_utils.file_write_format(file, "repairing service ..." )
                # restart service if check found the start status is abnormal
                repair_bugs(export_file,repair_times,serviceName,service_url,token)
            else:
                common_utils.file_write_format(file, "check result : normal")


        common_utils.file_write_format(file, 'check and repair service start status finished!')
        file.close()

    except:
        common_utils.file_write_format(file, "check arcgis server service start status failed!")
        file.close()
        return

# this method will try many times(descided by repair_times param) to repair the bug.
def repair_bugs(repair_times, serviceName, service_url, token):
    try:
        result = ""
        for j in range(repair_times):
            result = restart_service(serviceName, service_url, token)
            # print("result:", result)
            if (result == "success"):
                print('restart service success!')
                return result

        if result != "success":
            print('trying to restart service failed, please inform administrator to help repair this problem!')

        return result

    except:
        print( "try to repair the bug failed!")
        return "failed"

# method for restart arcgis server service
def restart_service(service_Name,url,token):
    try:

        # print("restart service...")
        stop_url = url + "/stop"
        start_url = url + "/start"
        params = {'token': token, 'f': 'json'}
        response = common_utils.submit_request(stop_url, params)
        status_stop = response[1]["status"]
        # print("stop",service_Name,"service",status_stop,"!")
        if status_stop == "success":
            response = common_utils.submit_request(start_url,params)
            status_start = response[1]["status"]
            # print("start",service_Name,"service",status_start,"!")
        return response[1]["status"]
    except:
        print("restart the arcgis server services failed!")
        return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))