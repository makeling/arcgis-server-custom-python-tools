#-*- coding: UTF-8 -*-
# !/usr/bin/python
__author__ = 'keling ma'

import os,json,sys
import time
import common_utils

print("let's start!")

export_file = common_utils.generate_export_file()

current_path = os.getcwd()
server_config = current_path + os.sep + 'batch_delete_service_tool/ags_pms.conf'

