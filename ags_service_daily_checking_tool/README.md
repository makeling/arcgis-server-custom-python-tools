# ags_service_daily_checking_tool

This script is a simple tool for checking the services status that hosted in arcgis server on every day.

If you are an administrator of arcgis server in your organization and you have published hundreds of services in your arcgis server big cluster.
Some services maybe not start  or some machine maybe don't create service instances as desired config. How to check become a really tough thing, this tool is just developed for solve this probem.

Fundamentally, this tool include two functions:

1. checking arcgis server service start status in a cluster multimachine deployment.
2. checking the instance numbers ensure every machine have created instance process follow the minimum settings in the service config.

## Requirement environment:

The python script developed in Python 3.6.1 |Anaconda custom (64-bit) .

## Usage:

1. edit the items in the ags_pms.conf file with your actual value.
{
"conns":{
"url":"http://192.168.100.124:6080/arcgis",
"username":"siteadmin",
"password":"123456"
},
"settings":{
"repair_times":3
}
}

repair_times: means the times that the tool would try to restart the service if found any problem. You could change the value based on your requirement,
but you should know more times will consume more resources for arcgis server machine to restart the service.

2. execute in a cmd:

$ cd <download path>/arcgis-server-custom-python-tools/ags_service_daily_checking_tool
$ python ags_service_daily_checking_tool.py

Please input service.json path and ags_pms.config path, eg: -a 'c:\\Users\maklmac\Desktop\ags_pms.conf' .
If you don't set , the default value would use the same path with the python script exist.
-a : The path of ags_pms.conf(optional)

let's start!
server_config .../arcgis-server-custom-python-tools/ags_service_daily_checking_tool/ags_pms.conf

{'url': 'http://192.168.100.124:6080/arcgis', 'username': 'siteadmin', 'password': '123456'}
{'repair_times': 3}
export_file: .../arcgis-server-custom-python-tools/ags_service_daily_checking_tool/check_results/check_result_20180312171345.txt
http://192.168.100.124:6080/arcgis/admin/generateToken
All the folders: ['/', 'f10', 'f20', 'ftt']
services_count: 115
start checking service status....

......

If you see the export informations like this, congratulation!

The checking result also be saved on <the_same_path_with_tool>\check_results\ folders, you could use them at any time.













