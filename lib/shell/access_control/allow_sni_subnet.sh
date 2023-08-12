#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/os/os_utils.sh

echo -e "${B_GREEN}>> Allow OUTGOING connections to $1 ${RESET}"

FAKE_SNI_IPV4=($(dig @1.1.1.1 +short $1))

for ip in "${FAKE_SNI_IPV4[@]}"; do
    FAKE_SNI_CIDR="${ip%.*}.0/24"
    echo -e "${B_GREEN}>> Allow SNI IPv4 Subnet $FAKE_SNI_CIDR ${RESET}"
    # Add it above the georestriction rules to make it an exception
    LINENUM_IPV4=$(iptables -L FORWARD --line-numbers | grep 'Drop OUTGOING to IR and CN' | awk '{print $1}')
    iptables -I FORWARD $LINENUM_IPV4 -d "${FAKE_SNI_CIDR}" -m conntrack --ctstate NEW,ESTABLISHED -m comment --comment "Allow SNI Subnet" -j ACCEPT
    LINENUM_IPV4=$(iptables -L OUTPUT --line-numbers | grep 'Drop OUTGOING to IR and CN' | awk '{print $1}')
    iptables -I OUTPUT $LINENUM_IPV4 -d "${FAKE_SNI_CIDR}" -m conntrack --ctstate NEW,ESTABLISHED -m comment --comment "Allow SNI Subnet" -j ACCEPT
done

FAKE_SNI_IPV6=($(dig @1.1.1.1 +short AAAA $1))

for ip in "${FAKE_SNI_IPV6[@]}"; do
    echo -e "${B_GREEN}>> Allow SNI IPv6 $ip ${RESET}"
    # Add it above the georestriction rules to make it an exception
    LINENUM_IPV6=$(ip6tables -L FORWARD --line-numbers | grep 'Drop OUTGOING to IR and CN' | awk '{print $1}')
    if [ -n "$LINENUM_IPV6" ]; then
        ip6tables -I FORWARD $LINENUM_IPV6 -d "${ip}" -m conntrack --ctstate NEW,ESTABLISHED -m comment --comment "Allow SNI Subnet" -j ACCEPT
    else
        ip6tables -I FORWARD -d "${ip}" -m conntrack --ctstate NEW,ESTABLISHED -m comment --comment "Allow SNI Subnet" -j ACCEPT
    fi
    LINENUM_IPV6=$(ip6tables -L OUTPUT --line-numbers | grep 'Drop OUTGOING to IR and CN' | awk '{print $1}')
    if [ -n "$LINENUM_IPV6" ]; then
        ip6tables -I OUTPUT $LINENUM_IPV6 -d "${ip}" -m conntrack --ctstate NEW,ESTABLISHED -m comment --comment "Allow SNI Subnet" -j ACCEPT
    else
        ip6tables -I OUTPUT -d "${ip}" -m conntrack --ctstate NEW,ESTABLISHED -m comment --comment "Allow SNI Subnet" -j ACCEPT
    fi
done

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
