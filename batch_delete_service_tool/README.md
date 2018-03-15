# batch_delete_service_tool

This tool developed for batch delete arcgis server services.


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
    "services_list":[],
    "folder":"/",
    "service_name_prefix":""
    }
  }
  ````

**services_list:** A list include all the services that you want to delete. This value should be set null if you want delete obey service_name_prefix or folder.
**folder:** If you want delete some services in specific folder, you should set this value, eg: "folder":"/", it means loop and delete all the services under the root folder. If the value keep null , the program would loop and delete all the services in any folder .
**service_name_prefix:" This param be used to filter the services name match the service_name_prefix.

2. execute in a cmd:

  ````
  $ cd <download path>/arcgis-server-custom-python-tools/batch_delete_service_tool

  $ python batch_delete_service_tool.py

  let's start!

  -------------------------creating export result file-------------------------

  update time：2018-03-15 17:19:13
  export_file: /Users/maklmac/GitHub/arcgis-server-custom-python-tools/batch_delete_service_tool/check_results/result_20180315171913.txt
  ags_pms.conf: /Users/maklmac/GitHub/arcgis-server-custom-python-tools/batch_delete_service_tool/ags_pms.conf

  conns:{'url': 'http://192.168.100.124:6080/arcgis', 'username': 'siteadmin', 'password': '123456'}
  settins:{'services_list': [], 'folder': '/', 'service_name_prefix': ''}
  http://192.168.100.124:6080/arcgis siteadmin 123456 [] /

  -------------------------generating token-------------------------

  token url: http://192.168.100.124:6080/arcgis/admin/generateToken
  tokenwp79jfOxNt4S6L-qQGz_qd9gpQeCxMs15w6DRHF-klDJybHqZj8kUSZNe-WiKvii

  -------------------------getting full service list-------------------------

  All the folders:['/', 'f10', 'f20', 'f30', 'ftt']
  services_count:47
  0

  -------------------------start delete service-------------------------

  service_url:http://192.168.100.124:6080/arcgis/admin/services/china73.MapServer/delete
  response time: 0.283118s
  delete result:{'status': 'success'}

  service_url:http://192.168.100.124:6080/arcgis/admin/services/china74.MapServer/delete
  response time: 0.559018s
  delete result:{'status': 'success'}

  service_url:http://192.168.100.124:6080/arcgis/admin/services/china75.MapServer/delete
  response time: 0.635703s
  delete result:{'status': 'success'}

  ......
  ````

If you see the export informations like this, congratulations!

The results also be saved in the folder of <the_same_path_with_tool>\check_results\ , you could use them at any time.













