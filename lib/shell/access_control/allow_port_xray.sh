#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/os/os_utils.sh

# Grab the interface name
INTERFACE=$(ip route get '8.8.8.8' | awk '{print $5}')

# Grab the line number of the rule that has the comment 'Drop Invalid Packets'
LINENUM_IPV4=$(iptables -L INPUT --line-numbers | grep 'Drop Invalid Packets' | awk '{print $1}')
LINENUM_IPV6=$(ip6tables -L INPUT --line-numbers | grep 'Drop Invalid Packets' | awk '{print $1}')

echo -e "${B_GREEN}>> Allow port 443/tcp for REALITY ${RESET}"
iptables -I INPUT $LINENUM_IPV4 -p tcp --dport 443 -m conntrack --ctstate NEW -m comment --comment "Allow REALITY" -j ACCEPT
ip6tables -I INPUT $LINENUM_IPV6 -p tcp --dport 443 -m conntrack --ctstate NEW -m comment --comment "Allow REALITY" -j ACCEPT

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
