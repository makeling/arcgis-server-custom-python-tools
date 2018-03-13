import sys
import json
import requests
import os
import getopt
import time

def main(argv=None):
    # Ask for the path for ags_pms.config file.
    opts, args = getopt.getopt(argv, "s:a:")
    config_file = ""
    server_config = ""
    if len(opts) == 0:
        print(
            "Please input the ags_pms.config path, eg: -a 'c:\\\\Users\\maklmac\\Desktop\\ags_pms.conf' . "
        )
        print("If you don't set , the default value would use the same path with the python script exist. ")
        print('-a : The path of ags_pms.conf(optional)')

        print("")
        print("let's start!")

    for op, value in opts:
        print("op:", op, "value: ", value)
        if op == "-a":
            server_config = value

    current_path = os.getcwd()

    if server_config == "":
        server_config = current_path + os.sep + 'ags_pms.conf'
        print("server_config", server_config)

    print("")

    conns = get_server_conns_params(server_config)

    if conns != None:
        url = conns['url']
        username = conns['username']
        password = conns['password']
    else:
        return

    settings = get_config_params(server_config)

    if settings != None:
        repair_times = settings['repair_times']

    else:
        return

    export_file = create_result_file(current_path)

    print("export_file:",export_file)

    token = generate_token(url, username, password)

    service_num,service_list = get_services_list(export_file,url,token)

    check_service_status(export_file,url,token,service_list,int(repair_times))

    check_instance_statistics(export_file,url,token,service_list,int(repair_times))

# create a new dir in the current path for store the check result file.
def create_result_file(current_path):
    try:
        export_result_folder = current_path + os.sep + "check_results"
        if os.path.exists(export_result_folder) == False:
            os.mkdir(export_result_folder)
        timeStamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

        export_file = export_result_folder + os.sep + "check_result_" + timeStamp + ".txt"

        # print(export_file)

        file = open(export_file, 'w')

        time_log = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        file.write("检测时间：" + time_log + "\n" + "\n")

        file.close()
        # export_result_name = service_status

        return export_file
    except:
        print("create the check_results folder or result file failed!")
        return

# get folder list and services list in every folder.
def get_services_list(export_file,url,token):
    try:
        file = open(export_file, 'a+')
        file.write("正在获取服务列表..."  + "\n")

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

        print("All the folders:", folders)
        file.write("返回所有文件夹：" + str(folders) + "\n")

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
        print("services_count:", count)
        file.write("当前server站点中的服务总数："+ str(count) + "个" + "\n")
        file.write("\n")

        file.close()
        return count, services_list
    except:
        print("get services list failed!")
        return

#check service instance status, then return error list and try to repair by restart service.
def check_instance_statistics(export_file,url,token,service_list,repair_times):
    try:
        file = open(export_file, 'a+')

        error_log = "位于{0}目录下的服务{1}在服务器{2}创建实例异常: 应创建最小实例数：{3}, 实际创建实例数：{4}。\n服务地址：{5} \n"

        error_services = {}

        print("start checking instance statistics... ")
        file.write("开始检测服务实例数状态..." + "\n")


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

            responsetime, service_detail = submit_request(service_url,params)

            # print(service_detail)

            min_instance_config = service_detail['minInstancesPerNode']

            stat_url = service_url + "/statistics"

            response = submit_request(stat_url, params)

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
                        print(error_log.format(folder, serviceName, machineName, min_instance_config, running_ins,
                                               service_url))
                        file.write(error_log.format(folder, serviceName, machineName, min_instance_config, running_ins,
                                               service_url))
                        file.write("\n")

                        error_services[serviceName] = service_url

        file.close()

        if len(error_services.keys()) > 0 :
            file = open(export_file, "a+")
            file.write("检测完毕，接下来将按照错误清单重启服务修复实例..." + "\n")
            for service in error_services.keys():
                serviceName = service
                service_url = error_services[service]

                repair_bugs(export_file,repair_times,serviceName,service_url,token)


            file.write("修复服务实例状态已完毕。" + "\n")
            print("repair instance status finished!")
            file.write("\n")

            file.close()

        file = open(export_file, "a+")
        file.write("检测实例状态已完毕。" + "\n")
        file.write("\n")

        file.close()
        print("check instance status finished!")

    except:
        print("check instanse failed!")
        return


#check service status, then export the status list and try to repair the bug.
def check_service_status(export_file,url,token,service_list,repair_times):
    try:
        error_log = "位于{0}目录下的服务{1}启动异常: 配置状态：{2}, 实际状态：{3}。\n服务地址：{4} \n"

        file = open(export_file, 'a+')

        print("start checking service status....")
        file.write("开始检测服务启动状态..." + "\n")

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

            check_url = service_url + "/status"

            params = {'token': token, 'f': 'json'}

            response = submit_request(check_url,params)

            status = response[1]

            configuredState = status['configuredState']
            realTimeState = status['realTimeState']

            if configuredState != realTimeState:
                print(error_log.format(folder, serviceName, configuredState, realTimeState, service_url))
                file.write(error_log.format(folder, serviceName, configuredState, realTimeState, service_url))
                file.write("\n")

                # restart service if check found the start status is abnormal
                repair_bugs(export_file,repair_times,serviceName,service_url,token)

        file.write("检测和修复服务启动状态已完毕。" + "\n")
        file.write("\n")
        file.close()
        print("check service start status finished!")
    except:
        print("check arcgis server service start status failed!")
        return

# this method will try many times(descided by repair_times param) to repair the bug.
def repair_bugs(export_file, repair_times, serviceName, service_url, token):
    try:
        file = open(export_file, 'a+')
        result = ""
        file.write("开始尝试重启服务" + serviceName + "..." + "\n")

        for j in range(repair_times):
            result = restart_service(serviceName, service_url, token)
            if (result == "success"):
                file.write("重启服务已成功！" + "\n")
                return

        if result != "success":
            print("尝试重新启动服务始终失败，请联系管理员介入辅助修复问题！")
            file.write("尝试重新启动服务始终失败，请联系管理员介入辅助修复问题！" + "\n")

        file.write("\n")
        file.close()
    except:
        print("try to repair the bug failed!")
        return

# method for restart arcgis server service
def restart_service(service_Name,url,token):
    try:
        print("restart service...")
        stop_url = url + "/stop"
        start_url = url + "/start"
        params = {'token': token, 'f': 'json'}
        response = submit_request(stop_url, params)
        status_stop = response[1]["status"]
        print("stop",service_Name,"service",status_stop,"!")
        if status_stop == "success":
            response = submit_request(start_url,params)
            status_start = response[1]["status"]
            print("start",service_Name,"service",status_start,"!")
        return response[1]["status"]
    except:
        print("restart the arcgis server services failed!")
        return

# method for get the connection parameters from a json file
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
        print("open ags_pms.conf file failed, please check the path.")
        return

# method for get the config parameters from a json file
def get_config_params(config_file):
    try:
        file = open(config_file)
        params = json.load(file)
        # print(params)
        settings = params['settings']
        print(settings)
        file.close()
        return settings
    except:
        print("open ags_pms.conf file failed, please check the path.")
        return


# print a dash line for format the different printing part.
def printSplitLine(comment):
    print("")
    splitline = ""
    count = 0
    for i in range(50):
        splitline += "-"
        count += 1
        if count == 25:
            splitline += comment

    print(splitline + "\n")

# generate token by arcgis server
def generate_token(url, username, password):
    try:
        tokenUrl = url + '/admin/generateToken'
        print(tokenUrl)
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))