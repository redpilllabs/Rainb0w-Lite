#!/bin/bash
source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/base/config.sh

function fn_check_for_pkg() {
    if [ $(dpkg-query -W -f='${Status}' $1 2>/dev/null | grep -c "ok installed") -eq 0 ]; then
        echo false
    else
        echo true
    fi
}

function fn_check_and_install_pkg() {
    local IS_INSTALLED=$(fn_check_for_pkg $1)
    if [ $IS_INSTALLED = false ]; then
        echo -e "${B_GREEN}>> Installing '$1'... ${RESET}"
        apt install -y $1
    fi
}

function fn_check_and_remove_pkg() {
    local IS_INSTALLED=$(fn_check_for_pkg $1)
    if [ $IS_INSTALLED = true ]; then
        echo -e "${B_GREEN}>> Removing '$1'... ${RESET}"
        apt remove -y $1
        apt autoremove -y
    fi
}

function fn_install_required_packages() {
    echo -e "${B_GREEN}>> Checking for requried packages${RESET}"
    source $PWD/lib/shell/os/upgrade_os.sh
    fn_check_and_install_pkg build-essential
    fn_check_and_install_pkg autoconf
    fn_check_and_install_pkg pkg-config
    fn_check_and_install_pkg dkms
    fn_check_and_install_pkg curl
    fn_check_and_install_pkg unzip
    fn_check_and_install_pkg qrencode
    fn_check_and_install_pkg openssl
    fn_check_and_install_pkg bc
    fn_check_and_install_pkg logrotate
    fn_check_and_install_pkg iptables-persistent
    fn_check_and_install_pkg python3-pip
    fn_check_and_install_pkg python3-venv
    fn_check_and_install_pkg rsyslog
    fn_check_and_install_pkg dnsutils
}

function fn_init_python_venv() {
    echo -e "${B_GREEN}>> Initializing Python venv with required modules${RESET}"
    venv_path="$PWD/.venv"
    python3 -m venv --system-site-packages "$venv_path"
    source "${venv_path}/bin/activate"
    pip3 install -r $PWD/requirements.txt
}

function fn_activate_python_venv() {
    venv_path="$PWD/.venv"
    if [ -d "$venv_path" ]; then
        source "${venv_path}/bin/activate"
    else
        echo -e "${B_GREEN}>> Activating Python environment${RESET}"
        fn_init_python_venv
    fi
}
