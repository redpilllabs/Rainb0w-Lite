#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Allow execution permission
find $PWD -name "*.sh" -exec chmod +x {} \;

source $PWD/lib/shell/base/colors.sh
source $PWD/lib/shell/base/config.sh
source $PWD/lib/shell/os/os_utils.sh
source $PWD/lib/shell/cryptography/gen_x25519_keys.sh

trap '' INT

# OS check
if ! [[ "$DISTRO" =~ "Ubuntu" || "$DISTRO" =~ "Debian" ]]; then
    echo "$DISTRO"
    echo -e "${B_RED}This installer only supports Debian and Ubuntu OS!${RESET}"
    exit 0
else
    # Version check
    if [[ "$DISTRO" =~ "Ubuntu" ]]; then
        if [ ! "$DISTRO_VERSION" == "20.04" ] && [ ! "$DISTRO_VERSION" == "22.04" ]; then
            echo "Your version of Ubuntu is not supported! Only 20.04 and 22.04 versions are supported."
            exit 0
        fi
    elif [[ "$DISTRO" =~ "Debian GNU/Linux" ]]; then
        if [ ! "$DISTRO_VERSION" == "11" ]; then
            echo "Your version of Debian is not supported! Minimum required version is 11"
            exit 0
        else
            # Debian has a quirk that usually comes with an old Kernel without
            # the corresponding headers and modules package available, therefore
            # we need to upgrade to the latest kernel available on the repository first
            apt update
            current_kernel=$(uname -r)
            latest_kernel=$(apt-cache search linux-image | grep -oP '5\.10\.[0-9]+-[0-9]+' | uniq | sort --version-sort | tail -n 1)
            if [[ "$latest_kernel" > "$current_kernel" ]]; then
                fn_check_and_install_pkg linux-image-$latest_kernel-amd64
                fn_check_and_install_pkg linux-headers-$latest_kernel-amd64
                echo -e "${B_GREEN}\n\nA newer kernel '$latest_kernel' is installed on your Debian.${RESET}"
                echo -e "${B_RED}You're server is now going to reboot to load the new kernel and the extra modules required${RESET}"
                echo -e "${B_GREEN}After booting up, run the script again with the following commands to proceed!${RESET}"
                echo -e "${B_YELLOW}cd Rainb0w-Lite"
                echo -e "./run.sh${RESET}"
                systemctl reboot
                exit
            fi
        fi
    fi
fi

# Check for root permissions
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./run.sh)"
    exit
fi

# Install packages
if [ ! -d "$HOME/Rainb0w_Lite_Home" ]; then
    MEMORY_SIZE=$(free -m | awk '/Mem:/ { print $2 }')
    if [ $MEMORY_SIZE -lt 512 ]; then
        local IS_INSTALLED=$(fn_check_for_pkg zram-tools)
        if [ $IS_INSTALLED = false ]; then
            echo -e "${B_YELLOW}You seem to be short on memory! Installing Zram to optimize memory...${RESET}"
            source $PWD/lib/shell/performance/enable_zram.sh
        fi
    fi
    # Install required packages
    fn_install_required_packages
    # Install xtables geoip
    source $PWD/lib/shell/os/install_xt_geoip.sh
    # Install Docker
    source $PWD/lib/shell/os/install_docker.sh
    # Reboot if needed
    source $PWD/lib/shell/os/check_reboot_required.sh
fi

function clear_and_copy_files() {
    # Cleanup and copy all the template files to let the admin select among them
    rm -rf $HOME/Rainb0w_Lite_Home
    mkdir $HOME/Rainb0w_Lite_Home
    cp -r ./Docker/* $HOME/Rainb0w_Lite_Home/
}

function installer_menu() {
    echo -ne "
Rainb0w Lite Proxy Installer v${VERSION}
Red Pill Labs

* Install:    Deploys a new configuration of proxies (REALITY, Hysteria, MTProto)
* Restore:    Restore a previous installation's configuration and users

Select installation type:

${B_GREEN}1)${RESET} Install
${B_GREEN}2)${RESET} Restore
${B_RED}0)${RESET} Exit

Choose an option: "
    read -r ans
    case $ans in
    2)
        clear
        # Move the files in place
        clear_and_copy_files
        python3 $PWD/lib/configurator.py "Restore"
        PYTHON_EXIT_CODE=$?
        if [ $PYTHON_EXIT_CODE -ne 0 ]; then
            echo "Python configurator did not finish successfully!"
            rm -rf $HOME/Rainb0w_Lite_Home
            exit
        fi
        source $PWD/lib/shell/deploy.sh "Restore"
        ;;
    1)
        clear
        # Move the files in place
        clear_and_copy_files
        # Prepare the x25519 keys for REALITY
        fn_gen_insert_x25519_keys
        python3 $PWD/lib/configurator.py "Install"
        PYTHON_EXIT_CODE=$?
        if [ $PYTHON_EXIT_CODE -ne 0 ]; then
            echo "Python configurator did not finish successfully!"
            rm -rf $HOME/Rainb0w_Lite_Home
            exit
        fi
        source $PWD/lib/shell/deploy.sh "Install"
        ;;
    0)
        exit
        ;;
    *)
        fn_fail
        clear
        installer_menu
        ;;
    esac
}

function main() {
    if [ -d "$HOME/Rainb0w_Lite_Home" ]; then
        # We have an existing installation, so let's present the dashboard to change settings
        python3 $PWD/lib/dashboard.py
        PYTHON_EXIT_CODE=$?
        if [ $PYTHON_EXIT_CODE -eq 1 ]; then
            source $PWD/lib/shell/docker/restart_all_containers.sh
            exit
        else
            exit
        fi
    else
        # This is a new installation
        installer_menu
    fi
}

clear
main
