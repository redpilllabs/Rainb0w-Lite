#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/os/os_utils.sh

echo -e "${B_GREEN}>> Removing previously set SNI subnets${RESET}"

tables=("FORWARD" "OUTPUT")

for table in "${tables[@]}"; do
    rule_numbers=$(iptables -L $table -n --line-numbers | grep -i "Allow SNI Subnet" | awk '{print $1}')
    for rule_number in $rule_numbers; do
        iptables -D "${table}" $rule_number
    done
done

for table in "${tables[@]}"; do
    rule_numbers=$(ip6tables -L $table -n --line-numbers | grep -i "Allow SNI Subnet" | awk '{print $1}')
    for rule_number in $rule_numbers; do
        ip6tables -D "${table}" $rule_number
    done
done

# Save changes
iptables-save | tee /etc/iptables/rules.v4 >/dev/null
ip6tables-save | tee /etc/iptables/rules.v6 >/dev/null
