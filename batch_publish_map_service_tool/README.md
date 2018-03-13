# batch_publish_map_service_tool

This tool can be used to batch publish arcgis server map services for test.

## Requirement environment:

1. The python script developed in Python 3.6.1 |Anaconda custom (64-bit) .

2. Generate a msd file in arcmap and ensure saved with relative path for the data source. Copy msd and data source to a share path ensure can be accessed by arcgis server account.

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
    "folder":"/",
    "start_num":0,
    "service_count":5,
    "service_name_prefix":"china",
    }
   }
  ````

**folder:** If you want to create a new folder then publish map service to this folder ,you could change the value to a new foler name. The default value is "/", means publish service to root dir.
**start_num** It is a start sequence code for automatic generate service name.
**service_count** This means how many services do you want to publish.
**service_name_prefix** The value would be used as the prefix of the service name.

Base on the sample settings, the services name list would be: china0.mapserver, china1.mapserver, china2.mapserver, china3.mapserver, china4.mapserver, china5.mapserver.

2. open the service.json file in a notepad, then edit the next key items:
  ````
  "properties": {
   "maxBufferCount": "100",
   "virtualCacheDir": "http://agsserver122:6080/arcgis/server/arcgiscache",
   "maxImageHeight": "2048",
   "maxRecordCount": "1000",
   "filePath": "\\\\192.168.100.124\\arcgisserver\\data\\china.msd",
   "maxImageWidth": "2048",
   "cacheOnDemand": "false",
   "virtualOutputDir": "http://agsserver122:6080/arcgis/server/arcgisoutput",
   "outputDir": "\\\\192.168.100.124\\arcgisserver\\directories\\arcgisoutput",
   "supportedImageReturnTypes": "MIME+URL",
   "isCached": "false",
   "ignoreCache": "false",
   "clientCachingAllowed": "false",
   "cacheDir": "\\\\192.168.100.124\\arcgisserver\\directories\\arcgiscache"
 },
  ````
 replace the value of keys "virtualCacheDir", "filePath", "virtualOutputDir", "outputDir", "cacheDir" to your actual values.


3. execute in a cmd:

  ````
  $ cd <download path>/arcgis-server-custom-python-tools/ags_service_daily_checking_tool

  $ python batch_publish_map_service_tool.py

  Please input service.json path and ags_pms.config path, eg: -s 'c:\\Users\maklmac\Desktop\service.json' -a 'c:\\Users\maklmac\Desktop\ags_pms.conf' .
  If you don't set , the default value would use the same path with the python script exist.
  -s : The path of service.json(optional)
  -a : The path of ags_pms.conf(optional)

  let's start!
  config_file /Users/maklmac/GitHub/arcgis-server-custom-python-tools/batch_publish_map_service_tool/service.json
  server_config /Users/maklmac/GitHub/arcgis-server-custom-python-tools/batch_publish_map_service_tool/ags_pms.conf

  {'url': 'http://192.168.100.124:6080/arcgis', 'username': 'siteadmin', 'password': '123456'}
  {'folder': '/', 'start_num': 0, 'service_count': 5, 'service_name_prefix': 'china'}

  -------------------------publish and start map service : china0-------------------------

  publishing service ...
  request url: http://192.168.100.124:6080/arcgis/admin/services/
  response result:  ('0.896946s', {'status': 'success'})
  starting service ...
  request url: http://192.168.100.124:6080/arcgis/admin/services/china0.MapServer/start
  response result:  ('0.578127s', {'status': 'success'})

  ......
  ````

If you see the export informations like this, congratulations!















