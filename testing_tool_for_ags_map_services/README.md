# testing_tool_for_ags_services

This tool developed for test the arcgis server map service validation check. The tool would random generate bbox and random select the test services from arcgis server site.
It's more efficient and convenient than test every service one by one.


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
    "interval":1,
    "request_times":10
    }
  }
  ````

**interval:** means the sleep time between the two requests be submited.
**request_times:** means how many requests do you want to submit for this time. This value also equal how many random services would be selected for test.

2. execute in a cmd:

  ````
  $ cd <download path>/arcgis-server-custom-python-tools/testing_tool_for_ags_map_services

  $ python testing_tool_for_ags_services.py

  let's start!
  -------------------------creating export result file-------------------------

  update time：2018-03-14 14:03:25
  export_file: /Users/maklmac/GitHub/arcgis-server-custom-python-tools/testing_tool_for_ags_map_services/check_results/result_20180314140325.txt
  -------------------------initializing parameters-------------------------

  ags_pms.conf: /Users/maklmac/GitHub/arcgis-server-custom-python-tools/testing_tool_for_ags_map_services/ags_pms.conf

  conns:{'url': 'http://192.168.100.124:6080/arcgis', 'username': 'siteadmin', 'password': '123456'}
  settins:{'interval': 1, 'request_times': 10, 'loop': True}
  -------------------------generating token-------------------------

  http://192.168.100.124:6080/arcgis/admin/generateToken
  tokenQKjrzKjgPWflOmdxvUh9Ixm91yj1lWFQrxOSeH33GrOyJgWj2Q7LSqwhtvxjBgLG
  All the folders:['/', 'f10', 'f20', 'f30', 'ftt']
  services_count:119
  -------------------------start testing-------------------------

  selected service:{'folderName': '/', 'serviceName': 'china62', 'type': 'MapServer', 'description': 'my map service'}
  http://192.168.100.124:6080/arcgis/rest/services/china62/MapServer
  param_bbox:10220282.60904153,4278391.844723576,12169166.535650779,4620659.297289255
  response duration: 0.453081s
  response content: {'href': 'http://agsserver122:6080/arcgis/server/arcgisoutput/china62_MapServer/_ags_map81da74375030415faa1e2716665fd0d4.png', 'width': 400, 'height': 400, 'extent': {'xmin': 10220282.60904153, 'ymin': 3475083.6077017915, 'xmax': 12169166.535650779, 'ymax': 5423967.534311039, 'spatialReference': {'wkid': 102100, 'latestWkid': 3857}}, 'scale': 18414614.44574546}
  ......
  ````

If you see the export informations like this, congratulations!

The testing result also be saved in the folder of <the_same_path_with_tool>\check_results\ , you could use them at any time.













