#-*- coding: UTF-8 -*-
__author__ = 'keling ma'
# !/usr/bin/python

import requests
import os,json,sys
import time

# Defines the entry point into the script
def main(argv=None):
    # Ask for admin/publisher user name and password
    username = "siteadmin"
    password = "Super123"
    server_url = r"https://serverpc.esrichina.com/arcgis1051/admin"

    minInstances = 1
    maxInstances = 2

    token = generateToken(server_url,username,password)
    print("token:",token)

    # folder = input("Enter the folder name or ROOT for the root location: ")

    rootFolder = '/'

    updateServicesByFolder(server_url,token,rootFolder,minInstances,maxInstances)

#literal all the servcies in user folder
def literalUserFolder(url,token,root):
    folders = getFolders(url, token)
    folders.append(root)
    print(folders)

    for folder in folders:
        services = getServiceList(url, token, folder)
        print(services)


#update service instances by folder
def updateServicesByFolder(url, token,folder,minInstances,maxInstances):
    serviceList = getServiceList(url,token,folder)
    print("serviceList:", serviceList)
    print("succeed in getting services list!")
    count = 0

    for i in range(len(serviceList)):
        service = serviceList[i]
        count +=1
        if i >56 and count <= 80:
            fullSvcName = service['serviceName'] + "." + service['type']
            properties = getServiceProperties(url, token, fullSvcName)
            properties['minInstancesPerNode'] = minInstances
            properties['maxInstancesPerNode'] = maxInstances
            print("editing service", count, ": ", fullSvcName)
            jsonProp = json.dumps(properties)
            status = updateServiceProperties(url, token, fullSvcName, jsonProp)
            print("result:", status['status'])
            time.sleep(3)



    # for service in serviceList:
    #     count += 1
    #     if(count <= 50):
    #         fullSvcName = service['serviceName'] + "." + service['type']
    #         properties = getServiceProperties(url,token,fullSvcName)
    #         properties['minInstancesPerNode'] = minInstances
    #         properties['maxInstancesPerNode'] = maxInstances
    #         print("editing service",count,": ",fullSvcName)
    #         jsonProp = json.dumps(properties)
    #         status = updateServiceProperties(url,token,fullSvcName,jsonProp)
    #         print("result:",status['status'])
    #         time.sleep(3)

# get folder!
def getFolders(url,token):
    servicesUrl = url + "/services"

    params = {'token': token, 'f': 'json'}
    r = requests.post(servicesUrl, data=params, verify=False)

    if (r.status_code != 200):
        r.raise_for_status()
        print('get services error.')
        return
    else:
        data = r.text
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return
        # Extract service list from data
        result = json.loads(data)
        # print(result)
        folderList = result['folders']
        return folderList

# update service properties
def updateServiceProperties(url,token,serviceName,properties):
    serviceUrl = url + "/services/" + serviceName + "/edit"
    params = {'token': token, 'f': 'json', 'service': properties}
    r = requests.post(serviceUrl, data=params, verify=False)

    if (r.status_code != 200):
        r.raise_for_status()
        print('get services error.')
        return
    else:
        data = r.text
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return
        # getEditStatus
        status = json.loads(data)
        return status

# get service properties
def getServiceProperties(url,token,serviceName):
    serviceUrl = url+"/services/"+serviceName
    params = {'token': token, 'f': 'json'}
    r = requests.post(serviceUrl, data=params, verify=False)

    if (r.status_code != 200):
        r.raise_for_status()
        print('get services error.')
        return
    else:
        data = r.text
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return
        # Extract service properties from data
        properties = json.loads(data)
        return properties

# get service list in folder
def getServiceList(url,token,folder):
    # Construct URL to read folder
    if str.upper(folder) == "SYSTEM" or str.upper(folder) == "UTILITIES":
        print("this is esri system folder, omited!")
        return

    if folder == "/":
        folder = ""

    folderUrl = url + "/services/" + folder
    params = {'token': token, 'f': 'json'}
    r = requests.post(folderUrl, data=params, verify=False)

    if (r.status_code != 200):
        r.raise_for_status()
        print('get services error.')
        return
    else:
        data = r.text
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return
        # Extract service list from data
        result = json.loads(data)
        serviceList = result['services']
        return serviceList

# get token by arcgis server
def generateToken(url, username, password):
    tokenUrl = url + '/generateToken'
    print(tokenUrl)
    # , 'ip':'192.168.100.85'
    params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}

    r = requests.post(tokenUrl, data=params, verify=False)

    if (r.status_code != 200):
        r.raise_for_status()
        print('Error while fetching tokens from admin URL. Please check the URL and try again.')
        return
    else:
        data = r.text
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return
        # Extract the token from it
        token = json.loads(data)
        return token['token']

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