#!/bin/bash
source $PWD/lib/shell/base/colors.sh

if systemctl is-active --quiet systemd-resolved; then
    echo -e "${B_GREEN}>> Updating system DNS resolver by systemd-resolved${RESET}"
    if [ ! -f "/etc/systemd/resolved.conf.d/nostublistener.conf" ]; then
        echo -e "${B_GREEN}>> Setting up system for a local DNS resolver ${RESET}"
        if [ ! -d "/etc/systemd/resolved.conf.d" ]; then
            mkdir -p /etc/systemd/resolved.conf.d
        fi
        touch /etc/systemd/resolved.conf.d/nostublistener.conf
        nostublistener="[Resolve]\n
            DNS=172.18.0.53\n
            DNS=1.1.1.2\n
            DNS=2606:4700:4700::1112\n
            DNSStubListener=no"
        nostublistener="${nostublistener// /}"
        echo -e $nostublistener | awk '{$1=$1};1' | tee /etc/systemd/resolved.conf.d/nostublistener.conf >/dev/null
        mv /etc/resolv.conf /etc/resolv.conf.backup
        ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
        systemctl reload-or-restart systemd-resolved
        sleep 2
    fi
else
    fn_check_and_install_pkg resolvconf
    echo -e "${B_GREEN}>> Updating system DNS resolver by resolvconf${RESET}"
    if [ ! -d "/etc/resolvconf/resolv.conf.d/" ]; then
        mkdir -p /etc/resolvconf/resolv.conf.d/
        touch /etc/resolvconf/resolv.conf.d/head
    fi
    echo "nameserver 172.18.0.53" | tee /etc/resolvconf/resolv.conf.d/head
    echo "nameserver 1.1.1.2" | tee -a /etc/resolvconf/resolv.conf.d/head
    echo "nameserver 2606:4700:4700::1112" | tee -a /etc/resolvconf/resolv.conf.d/head
    cp /etc/resolv.conf /etc/resolv.conf.backup
    resolvconf -u
fi
