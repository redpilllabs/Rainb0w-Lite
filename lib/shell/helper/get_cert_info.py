#!/usr/bin/env python3


import os
import sys

import toml

# Load the TOML file
config_file_handle = open(
    f"{os.path.expanduser('~')}/Rainb0w_Lite_Home/rainb0w_config.toml", "r"
)
rainb0w_config = toml.load(config_file_handle)
proxy_name = str(sys.argv[1]).upper()

if rainb0w_config[proxy_name]["IS_ENABLED"]:
    print(rainb0w_config[proxy_name]["SNI"])

config_file_handle.close()
