#!/usr/bin/env python3


import os
import sys

import toml

# Load the TOML file
config_file_handle = open(
    f"{os.path.expanduser('~')}/Rainb0w_Lite_Home/rainb0w_config.toml", "r"
)
rainb0w_config = toml.load(config_file_handle)

if sys.argv[1] == "reality":
    print(rainb0w_config["REALITY"]["PORT"])
elif sys.argv[1] == "mtproto":
    print(rainb0w_config["MTPROTO"]["PORT"])
elif sys.argv[1] in ["hysteria"]:
    print(rainb0w_config["HYSTERIA"]["PORT"])
else:
    pass

config_file_handle.close()
