#!/bin/bash
source $PWD/lib/shell/base/colors.sh

if ! docker network list | awk '{print $2}' | grep -q '^proxy$'; then
    echo -e "${B_GREEN}>> Creating a shared Docker network ${RESET}"
    docker network create --subnet=172.18.0.0/16 proxy >/dev/null
fi
