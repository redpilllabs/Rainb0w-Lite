#!/bin/bash

VERSION="1.5"

# Platform
DISTRO="$(awk -F= '/^NAME/{print $2}' /etc/os-release)"
DISTRO_VERSION=$(echo "$(awk -F= '/^VERSION_ID/{print $2}' /etc/os-release)" | tr -d '"')

RAINB0W_HOME_DIR=$HOME/Rainb0w_Lite_Home
CLIENT_CONFIG_FILES_DIR=$RAINB0W_HOME_DIR/clients

# Proxy Status (only for holding temporary status for client info printing)
REALITY_ENABLED=false
MTPROTO_ENABLED=false
HYSTERIA_ENABLED=false
