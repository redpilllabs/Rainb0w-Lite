#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/docker/docker_utils.sh

echo -e "${B_GREEN}>> Pulling the latest Docker images${RESET}"

python3 $PWD/lib/shell/helper/get_proxy_status.py "blocky"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    docker pull spx01/blocky
fi

python3 $PWD/lib/shell/helper/get_proxy_status.py "xray"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    docker pull teddysun/xray
fi

python3 $PWD/lib/shell/helper/get_proxy_status.py "hysteria"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    docker pull tobyxdd/hysteria
fi

python3 $PWD/lib/shell/helper/get_proxy_status.py "mtproto"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    docker pull redpilllabs/mtprotopy
fi

source $PWD/lib/shell/docker/restart_all_containers.sh

echo -e "${B_GREEN}<< Finished updating! >>${RESET}"
