#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/os/os_utils.sh

### Args
# $1 -> Hysteria operation mode [QUIC, UDP]

# Grab the interface name
INTERFACE=$(ip route get '8.8.8.8' | awk '{print $5}')

# Grab the line number of the rule that has the comment 'Drop Invalid Packets'
LINENUM_IPV4=$(iptables -L INPUT --line-numbers | grep 'Drop Invalid Packets' | awk '{print $1}')
LINENUM_IPV6=$(ip6tables -L INPUT --line-numbers | grep 'Drop Invalid Packets' | awk '{print $1}')

echo -e "${B_GREEN}>> Allow port 8443/udp for Hysteria ${RESET}"
iptables -I INPUT $LINENUM_IPV4 -p udp --dport 8443 -m conntrack --ctstate NEW -m comment --comment "Allow Hysteria" -j ACCEPT
ip6tables -I INPUT $LINENUM_IPV6 -p udp --dport 8443 -m conntrack --ctstate NEW -m comment --comment "Allow Hysteria" -j ACCEPT

if [ ! $# -eq 0 ]; then
    if [ "$1" == 'QUIC' ]; then
        echo -e "${B_GREEN}>> Forward port 443/udp for QUIC on Hysteria ${RESET}"
        iptables -t nat -A PREROUTING -i $INTERFACE -p udp --dport 443 -j DNAT --to-destination :8443
        ip6tables -t nat -A PREROUTING -i $INTERFACE -p udp --dport 443 -j DNAT --to-destination :8443
    fi
fi

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
