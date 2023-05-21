#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/base/config.sh
source $PWD/lib/shell/os/os_utils.sh

### Args
# $1 -> Port number

# Grab the interface name
INTERFACE=$(ip route get '8.8.8.8' | awk '{print $5}')

# Grab the line number of the rule that has the comment 'Drop Invalid Packets'
LINENUM=$(iptables -L INPUT --line-numbers | grep 'Drop Invalid Packets' | awk '{print $1}')

echo -e "${B_GREEN}>> Allow port 993/tcp for MTProto ${RESET}"
iptables -I INPUT $LINENUM -p tcp --dport 993 -m conntrack --ctstate NEW -m comment --comment "Allow MTProto" -j ACCEPT
ip6tables -I INPUT $LINENUM -p tcp --dport 993 -m conntrack --ctstate NEW -m comment --comment "Allow MTProto" -j ACCEPT
if [ ! $# -eq 0 ]; then
    if [[ "$1" =~ ^[1-9][0-9]*$ ]]; then
        echo -e "${B_GREEN}>> Forward port $1/tcp for MTProto ${RESET}"
        iptables -t nat -A PREROUTING -i $INTERFACE -p tcp --dport $1 -j DNAT --to-destination :993
        ip6tables -t nat -A PREROUTING -i $INTERFACE -p tcp --dport $1 -j DNAT --to-destination :993
    fi
fi

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
