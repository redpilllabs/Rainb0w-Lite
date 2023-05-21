#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/base/config.sh
source $PWD/lib/shell/text/text_utils.sh
source $PWD/lib/shell/os/os_utils.sh
source $PWD/lib/shell/docker/docker_utils.sh

# Create Docker network
source $PWD/lib/shell/docker/init_vol_net.sh

# Apply Kernel's network stack optimizations
source $PWD/lib/shell/performance/tune_kernel_net.sh

# Setup firewall with necessary protections
source $PWD/lib/shell/access_control/setup_firewall.sh

# Check if user selected proxies that need DNS support
python3 $PWD/lib/shell/helper/get_proxy_status.py "blocky"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    # Disable DNS stub listener to free up the port 53 for blocky DNS
    source $PWD/lib/shell/os/disable_dns_stub_listener.sh
    fn_restart_docker_container "blocky"
fi

python3 $PWD/lib/shell/helper/get_proxy_status.py "xray"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    source $PWD/lib/shell/access_control/allow_port_xray.sh
    fn_restart_docker_container "xray"
    REALITY_ENABLED=true
fi

python3 $PWD/lib/shell/helper/get_proxy_status.py "mtproto"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    mtproto_extra_port=$(python3 $PWD/lib/shell/helper/get_mtproto_extra_port.py)
    source $PWD/lib/shell/access_control/allow_port_mtproto.sh $mtproto_extra_port
    fn_restart_docker_container "mtproto"
    MTPROTO_ENABLED=true
fi

python3 $PWD/lib/shell/helper/get_proxy_status.py "hysteria"
PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    hysteria_mode=$(python3 $PWD/lib/shell/helper/get_hysteria_mode.py)
    source $PWD/lib/shell/access_control/allow_port_hysteria.sh "$hysteria_mode"

    # Generate a self-signed x509 certificate for Hysteria
    output=$(python3 $PWD/lib/shell/helper/get_cert_info.py)
    common_name=$(echo $output | awk -F'[ :]' '{print $1}')
    source $PWD/lib/shell/cryptography/gen_x509_cert.sh ${common_name}

    # Add cronjob to renew the cert once a year
    if ! crontab -l | grep -q "0 1 * * * root bash /usr/libexec/rainb0w/renew_selfsigned_cert.sh >/tmp/renew_certs.log"; then
        echo -e "${B_GREEN}>> Adding cronjob to renew the selfsigned cert every year ${RESET}"
        cp $PWD/lib/shell/cronjobs/renew_selfsigned_cert.sh /usr/libexec/rainb0w/renew_selfsigned_cert.sh
        sed -i 's/COMMON_NAME=.*/COMMON_NAME="'"$common_name"'"/g' /usr/libexec/rainb0w/renew_selfsigned_cert.sh
        chmod +x /usr/libexec/rainb0w/renew_selfsigned_cert.sh
        (
            crontab -l
            echo "0 0 1 1 * root bash /usr/libexec/rainb0w/renew_selfsigned_cert.sh >/tmp/renew_certs.log"
        ) | crontab -
    fi
    fn_restart_docker_container "hysteria"
    HYSTERIA_ENABLED=true
fi

echo -e "\n\nYour proxies are ready now!\n"

if [ ! $# -eq 0 ]; then
    if [ "$1" == 'Install' ]; then
        username=$(python3 $PWD/lib/shell/helper/get_username.py)
        echo $(printf '=%.0s' {1..60})
        if [ "$REALITY_ENABLED" = true ]; then
            echo -e "\n*********************** Xray REALITY ***********************"
            cat ${CLIENT_CONFIG_FILES_DIR}/${username}/reality-url.txt
            echo -e "\n\n"
            qrencode -t ansiutf8 <"${CLIENT_CONFIG_FILES_DIR}/${username}/reality-url.txt"
        fi
        if [ "$MTPROTO_ENABLED" = true ]; then
            echo -e "\n*********************** MTProto ***********************"
            cat ${CLIENT_CONFIG_FILES_DIR}/${username}/mtproto-url.txt
            echo -e "\n\n"
            qrencode -t ansiutf8 <"${CLIENT_CONFIG_FILES_DIR}/${username}/mtproto-url.txt"
        fi
        if [ "$HYSTERIA_ENABLED" = true ]; then
            echo -e "\n*********************** Hysteria ***********************"
            cat ${CLIENT_CONFIG_FILES_DIR}/${username}/hysteria-url.txt
            echo -e "\n\n"
            qrencode -t ansiutf8 <"${CLIENT_CONFIG_FILES_DIR}/${username}/hysteria-url.txt"
        fi
        echo -e "\n"
        echo $(printf '=%.0s' {1..60})
        echo -e "\n
You can also find these QRCodes and pre-configured client.json files for '${username}' in the following paths:
${GREEN}${CLIENT_CONFIG_FILES_DIR}/${username}/${RESET}

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

echo -e "\n"
fn_typewriter "Women " $B_GREEN
fn_typewriter "Life " $B_WHITE
fn_typewriter "Freedom..." $B_RED
echo ""
fn_typewriter "#MahsaAmini " $B_WHITE
echo -e "\n"
