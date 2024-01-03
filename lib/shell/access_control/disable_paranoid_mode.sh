#!/bin/bash
source $PWD/lib/shell/base/colors.sh

modprobe xt_geoip
IS_MODULE_LOADED=$(lsmod | grep ^xt_geoip)
if [ ! -z "$IS_MODULE_LOADED" ]; then
    bash $PWD/lib/shell/os/install_xt_geoip.sh
fi

# Backup current iptables
mkdir $HOME/Rainb0w_Backup
iptables-save | tee $HOME/Rainb0w_Backup/rules.v4 >/dev/null
ip6tables-save | tee $HOME/Rainb0w_Backup/rules.v6 >/dev/null

echo -e "${B_GREEN}>> Allow non-Iranian incoming connections ${RESET}"
iptables -D INPUT -m geoip --src-cc IR -m comment --comment "Drop everything except Iran" -j ACCEPT
ip6tables -D INPUT -m geoip --src-cc IR -m comment --comment "Drop everything except Iran" -j ACCEPT

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
