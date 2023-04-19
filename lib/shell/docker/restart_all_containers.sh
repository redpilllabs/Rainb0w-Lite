#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/docker/docker_utils.sh

CONTAINERS=("blocky" "xray" "hysteria" "mtprotopy")

for container in "${CONTAINERS[@]}"; do
    fn_restart_docker_container $container
    sleep 1
done

echo -e "${B_GREEN}<< Finished applying changes! >>${RESET}"
