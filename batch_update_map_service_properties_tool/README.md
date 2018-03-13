# batch_update_map_service_properties_tool

The simple tool developed to automatic update arcgis server map service properties obey different rules.

## Requirement:

The python script developed in Python 3.6.1 |Anaconda custom (64-bit) .

## Usage:

1. edit the items in the ags_pms.conf file with your actual value.  

  ````
  {
    "conns":{
    "url":"http://192.168.100.124:6080/arcgis",
    "username":"siteadmin",
    "password":"123456"
  },
    "settings":{
    "services_list":["china0","china1","china2"],
    "properties":{"minInstancesPerNode":0,
    "maxInstancesPerNode":1},
    "folder":"",
    "service_name_prefix":""
    }
   }
  ````


**services_list:** A list include all the update service name, this value should be set null if you want update properties obey service_name_prefix.
**properties:** A dictionary include all the properties you want to update ,ensure keep the same key with the map service default returned, you could reference the properties key in service.json file to create a new one.
**folder:** If you want update some map services in specific folder, you could set this value, eg: "folder":"/", it means loop all the services under the root folder. If the value keep null , the program will loop all the services in any folder .
**service_name_prefix:" This param be used to filter the services name match the service_name_prefix.

> In fact , this tool include two modes, if you set services_list means you want precise update specific services. so , even you set folder and service_name_prefix, it doesn't work in this mode. If you need update more services obey the filter result of service_name_prefix, remember keep the value of service_list is null.

2. execute in a cmd:

  ````
  $ cd <download path>/arcgis-server-custom-python-tools/batch_update_map_service_properties_tool

  $ python batch_update_map_service_properties_tool.py

    let's start!

    -------------------------creating export result file-------------------------

    update time：2018-03-13 17:18:58
    export_file: /Users/maklmac/GitHub/arcgis-server-custom-python-tools/batch_update_map_service_properties_tool/check_results/result_20180313171858.txt

    -------------------------initializing parameters-------------------------

    ags_pms.conf: /Users/maklmac/GitHub/arcgis-server-custom-python-tools/batch_update_map_service_properties_tool/ags_pms.conf

    conns:{'url': 'http://192.168.100.124:6080/arcgis', 'username': 'siteadmin', 'password': '123456'}
    settins:{'services_list': ['china0', 'china1', 'china2'], 'properties': {'minInstancesPerNode': 0, 'maxInstancesPerNode': 1}, 'folder': '', 'service_name_prefix': ''}

    -------------------------generating token-------------------------

    token url: http://192.168.100.124:6080/arcgis/admin/generateToken
    tokenIka5D-RIdgTjjAEgaxEop4uvqH54to5ptLAX1dkpsVE9xHc8kwaqYCuCCjO3Eoan

    -------------------------getting full service list-------------------------

    All the folders:['/', 'f10', 'f20', 'f30', 'ftt']
    services_count:119
    ......
  ````

If you see the export informations like this, congratulations!

The result also be saved in the folder of <the_same_path_with_tool>\check_results\ , you could use them at any time.













