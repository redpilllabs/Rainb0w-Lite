#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/base/config.sh
source $PWD/lib/shell/os/os_utils.sh
source $PWD/lib/shell/docker/docker_utils.sh

# Install Docker and required packages
fn_check_and_install_pkg openssl
fn_check_and_install_pkg bc
fn_check_and_install_pkg logrotate
fn_check_and_install_pkg iptables-persistent
fn_check_and_install_pkg qrencode
source $PWD/lib/shell/os/install_docker.sh
source $PWD/lib/shell/docker/init_vol_net.sh
source $PWD/lib/shell/os/install_xt_geoip.sh

# Build a Docker image for MTProtoPy and check if the image was successfully buil
if [ ! "$(docker images -q mtprotopy)" ]; then
    docker buildx build --tag mtprotopy $HOME/Rainb0w_Lite_Home/mtprotopy/
    if [ ! "$(docker images -q mtprotopy)" ]; then
        echo -e "${B_RED}There was an issue when building a Docker image for 'MTProtoPy', check the logs!${RESET}"
        echo -e "${B_YELLOW}After resolving the issue, run the installer again.${RESET}"
        rm -rf $HOME/Rainb0w_Lite_Home
        exit
    fi
fi

# Apply Kernel's network stack optimizations
source $PWD/lib/shell/performance/tune_kernel_net.sh

# Get selected ports and allow them in iptables
output=$(python3 $PWD/lib/shell/helper/get_port.py "reality")
reality_port=$(echo $output | awk -F'[ :]' '{print $1}')
output=$(python3 $PWD/lib/shell/helper/get_port.py "mtproto")
mtproto_port=$(echo $output | awk -F'[ :]' '{print $1}')
output=$(python3 $PWD/lib/shell/helper/get_port.py "hysteria")
hysteria_port=$(echo $output | awk -F'[ :]' '{print $1}')
source $PWD/lib/shell/access_control/setup_firewall.sh $reality_port $mtproto_port $hysteria_port

# Disable DNS stub listener to free up the port 53
source $PWD/lib/shell/os/disable_dns_stub_listener.sh

# Generate a self-signed x509 certificate
output=$(python3 $PWD/lib/shell/helper/get_cert_info.py)
common_name=$(echo $output | awk -F'[ :]' '{print $1}')
organization=$(echo $output | awk -F'[ :]' '{print $2}')
source $PWD/lib/shell/cryptography/gen_x509_cert.sh ${common_name} ${organization}

# Add cronjob to renew the cert once a year
if ! crontab -l | grep -q "0 1 * * * root bash /usr/libexec/rainb0w/renew_selfsigned_cert.sh >/tmp/renew_certs.log"; then
    echo -e "${B_GREEN}>> Adding cronjob to renew the selfsigned cert every year ${RESET}"
    cp $PWD/lib/shell/cronjobs/renew_selfsigned_cert.sh /usr/libexec/rainb0w/renew_selfsigned_cert.sh
    sed -i 's/COMMON_NAME=.*/COMMON_NAME="'"$common_name"'"/g' /usr/libexec/rainb0w/renew_selfsigned_cert.sh
    sed -i 's/ORGANIZATION=.*/ORGANIZATION="'"$organization"'"/g' /usr/libexec/rainb0w/renew_selfsigned_cert.sh
    chmod +x /usr/libexec/rainb0w/renew_selfsigned_cert.sh
    (
        crontab -l
        echo "0 0 1 1 * root bash /usr/libexec/rainb0w/renew_selfsigned_cert.sh >/tmp/renew_certs.log"
    ) | crontab -
fi

# Start proxy containers one by one
CONTAINERS=("blocky" "xray" "hysteria" "mtprotopy")
for proxy in ${CONTAINERS[@]}; do
    fn_restart_docker_container $proxy
done

echo -e "\n\nYour proxies are ready now!\n"

if [ ! $# -eq 0 ]; then
    if [ "$1" == 'Install' ]; then
        username=$(python3 $PWD/lib/shell/helper/get_username.py)
        echo $(printf '=%.0s' {1..60})
        echo -e "\n*********************** Xray REALITY ***********************"
        cat ${CLIENT_CONFIG_FILES_DIR}/${username}/reality-url.txt
        echo -e "\n\n"
        qrencode -t ansiutf8 <"${CLIENT_CONFIG_FILES_DIR}/${username}/reality-url.txt"
        echo -e "\n*********************** MTProto ***********************"
        cat ${CLIENT_CONFIG_FILES_DIR}/${username}/mtproto-url.txt
        echo -e "\n\n"
        qrencode -t ansiutf8 <"${CLIENT_CONFIG_FILES_DIR}/${username}/mtproto-url.txt"
        echo -e "\n*********************** Hysteria ***********************"
        cat ${CLIENT_CONFIG_FILES_DIR}/${username}/hysteria-url.txt
        echo -e "\n\n"
        qrencode -t ansiutf8 <"${CLIENT_CONFIG_FILES_DIR}/${username}/hysteria-url.txt"
        echo -e "\n"
        echo $(printf '=%.0s' {1..60})
        echo -e "\n
You can also find these QRCodes and pre-configured client.json files for '${username}' in the following paths:
Xray REALITY:
    - JSON:   ${GREEN}${CLIENT_CONFIG_FILES_DIR}/${username}/reality.json${RESET}
    - QRCODE: ${GREEN}${CLIENT_CONFIG_FILES_DIR}/${username}/reality-qrcode.png${RESET}
Hysteria:
    - JSON:   ${GREEN}${CLIENT_CONFIG_FILES_DIR}/${username}/hysteria.json${RESET}
    - QRCODE: ${GREEN}${CLIENT_CONFIG_FILES_DIR}/${username}/hysteria-qrcode.png${RESET}
Use FTP clients, scp command, or even 'cat' them on the terminal and
then copy and paste to a local json file to provide to your client apps.

${B_YELLOW}NOTE: DO NOT SHARE THESE LINKS AND INFORMATION OVER SMS OR DOMESTIC MESSENGERS,
USE EMAILS OR OTHER SECURE WAYS OF COMMUNICATION INSTEAD!${RESET}
        "
    elif [ "$1" == 'Restore' ]; then
        echo -e "User share urls are the same as in your configuration, you can view them in the dashboard"
    else
        echo -e "Invalid mode supplied!"
    fi
fi

echo -e "\nYou can add/remove users or find more options in the dashboard,
in order to display the dashboard run the 'run.sh' script again.${RESET}"
