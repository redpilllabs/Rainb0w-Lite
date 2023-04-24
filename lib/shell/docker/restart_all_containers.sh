#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/docker/docker_utils.sh

fn_restart_docker_container "blocky"
CONTAINERS=("xray" "hysteria" "mtproto")
for container in "${CONTAINERS[@]}"; do
    python3 $PWD/lib/shell/helper/get_proxy_status.py $container
    PYTHON_EXIT_CODE=$?
    if [ $PYTHON_EXIT_CODE -ne 0 ]; then
        fn_restart_docker_container $container
        sleep 1
    fi
done

echo -e "${B_GREEN}<< Finished applying changes! >>${RESET}"
