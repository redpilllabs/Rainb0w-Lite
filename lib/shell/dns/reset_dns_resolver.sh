#!/bin/bash
source $PWD/lib/shell/base/colors.sh

echo -e "${B_GREEN}>> Resetting system DNS resolver back to default settings${RESET}"
if [ -f "/etc/resolv.conf.backup" ]; then
    rm /etc/resolv.conf
    mv /etc/resolv.conf.backup /etc/resolv.conf
fi

if systemctl is-active --quiet systemd-resolved; then
    if [ -f "/etc/systemd/resolved.conf.d/nostublistener.conf" ]; then
        rm /etc/systemd/resolved.conf.d/nostublistener.conf
    fi
    systemctl reload-or-restart systemd-resolved
    sleep 5
else
    if [ -f "/etc/resolvconf/resolv.conf.d/head" ]; then
        echo "" | tee /etc/resolvconf/resolv.conf.d/head
    fi
    resolvconf -u
fi
