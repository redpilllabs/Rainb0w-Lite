#!/usr/bin/env python3


import os
import re
import signal
from fileinput import FileInput
import sys
from time import sleep
from typing import List

from base.config import (
    BLOCKY_CONFIG_FILE,
    CLIENT_CONFIG_FILES_DIR,
    HYSTERIA_CONFIG_FILE,
    MTPROTOPY_CONFIG_FILE,
    RAINB0W_BACKUP_DIR,
    RAINB0W_CONFIG_FILE,
    RAINB0W_USERS_FILE,
    XRAY_CONFIG_FILE,
)
from pick import pick
from proxy.blocky import disable_porn_dns_blocking, enable_porn_dns_blocking
from proxy.mtproto import change_mtproto_adtag, prompt_mtproto_adtag, reset_mtproto_sni
from proxy.xray import reset_xray_sni
from rich import print
from user.user_manager import (
    add_user_to_proxies,
    create_new_user,
    gen_user_links_qrcodes,
    get_users,
    print_client_info,
    remove_user,
    reset_user_credentials,
    save_users,
)
from utils.ac_utils import is_porn_blocked
from utils.cert_utils import prompt_sni
from utils.helper import (
    clear_screen,
    copy_dir,
    copy_file,
    load_toml,
    prompt_clear_screen,
    save_toml,
)
from utils.os_utils import is_network_stack_tweaked, is_service_running, run_system_cmd

NEED_SERVICE_RESTART = False


def sni_menu():
    global NEED_SERVICE_RESTART

    title = "Select any option:"
    options = [
        "Change REALITY/Hysteria SNI",
        "Change MTProto SNI",
        "Back to Main Menu",
    ]
    option, _ = pick(options, title)
    if option == "Change REALITY/Hysteria SNI":
        clear_screen()
        rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)
        proxy_sni = prompt_sni("REALITY/Hysteria")
        print("Resetting the new SNI on REALITY and Hysteria")
        if rainb0w_config["XRAY"]["IS_ENABLED"]:
            rainb0w_config["XRAY"]["SNI"] = proxy_sni
            reset_xray_sni(proxy_sni, XRAY_CONFIG_FILE)
        if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
            rainb0w_config["HYSTERIA"]["SNI"] = proxy_sni
            run_system_cmd(
                [
                    f"{os.getcwd()}/lib/shell/cryptography/gen_x509_cert.sh",
                    proxy_sni,
                ]
            )
            with FileInput(
                "/usr/libexec/rainb0w/renew_selfsigned_cert.sh", inplace=True
            ) as file:
                for line in file:
                    if line.startswith("COMMON_NAME="):
                        line = f"COMMON_NAME={proxy_sni}"
                    print(line, end="")

        save_toml(rainb0w_config, RAINB0W_CONFIG_FILE)
        # Regenerate user links and QR codes with the new SNI
        print("Regenerating user share links and QR codes")
        rainb0w_users = get_users(RAINB0W_USERS_FILE)
        if rainb0w_users:
            for user in rainb0w_users:
                gen_user_links_qrcodes(user, RAINB0W_CONFIG_FILE)

        print("Applying firewall settings")
        #FIXME: Somehow the last remaining rule is not removed so we need to run this twice!
        run_system_cmd(
                [
                    f"{os.getcwd()}/lib/shell/access_control/remove_sni_subnet.sh"
                ]
            )
        run_system_cmd(
                [
                    f"{os.getcwd()}/lib/shell/access_control/remove_sni_subnet.sh"
                ]
            )
        run_system_cmd(
                [
                    f"{os.getcwd()}/lib/shell/access_control/allow_sni_subnet.sh",
                    proxy_sni,
                ]
            )


        NEED_SERVICE_RESTART = True
        print(
            "Changes only take effect after selecting 'Apply Changes' in the dashboard!"
        )
        prompt_clear_screen()
    elif option == "Change MTProto SNI":
        clear_screen()
        rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)
        proxy_sni = prompt_sni("MTProto")
        print("Resetting the new SNI on MTProto")
        if rainb0w_config["MTPROTO"]["IS_ENABLED"]:
            rainb0w_config["MTPROTO"]["SNI"] = proxy_sni
            reset_mtproto_sni(proxy_sni, MTPROTOPY_CONFIG_FILE)
            save_toml(rainb0w_config, RAINB0W_CONFIG_FILE)
            # Regenerate user links and QR codes with the new SNI
            print("Regenerating user share links and QR codes")
            rainb0w_users = get_users(RAINB0W_USERS_FILE)
            if rainb0w_users:
                for user in rainb0w_users:
                    gen_user_links_qrcodes(user, RAINB0W_CONFIG_FILE)

            NEED_SERVICE_RESTART = True
            print(
                "Changes only take effect after selecting 'Apply Changes' in the dashboard!"
            )
            prompt_clear_screen()
        else:
            print(
                "MTProto is not enabled. You need to enable MTProto during installation before changing the SNI."
            )
            prompt_clear_screen()
    dashboard()


def performance_menu():
    title = "Select any option to optimize performance:"
    options = [
        "Revert Network Stack Optimizations"
        if is_network_stack_tweaked()
        else "Optimize Network Stack (BBR)",
        "Disable Zram Swap" if is_service_running("zramswap") else "Enable Zram Swap",
        "Back to Main Menu",
    ]
    option, _ = pick(options, title)
    if option == "Optimize Network Stack (BBR)":
        run_system_cmd([f"{os.getcwd()}/lib/shell/performance/tune_kernel_net.sh"])
        prompt_clear_screen()
        performance_menu()
    elif option == "Revert Network Stack Optimizations":
        run_system_cmd([f"{os.getcwd()}/lib/shell/performance/revert_kernel_net.sh"])
        prompt_clear_screen()
        performance_menu()
    elif option == "Enable Zram Swap":
        run_system_cmd([f"{os.getcwd()}/lib/shell/performance/enable_zram.sh"])
        prompt_clear_screen()
        performance_menu()
    elif option == "Disable Zram Swap":
        run_system_cmd([f"{os.getcwd()}/lib/shell/performance/disable_zram.sh"])
        prompt_clear_screen()
        performance_menu()
    dashboard()


def mtproto_menu():
    global NEED_SERVICE_RESTART

    title = "Select any option:"
    options = [
        "Change/Remove AdTag",
        "Back to Main Menu",
    ]
    option, _ = pick(options, title)
    if option == "Change/Remove AdTag":
        clear_screen()
        adtag = prompt_mtproto_adtag()
        change_mtproto_adtag(RAINB0W_CONFIG_FILE, MTPROTOPY_CONFIG_FILE, adtag)
        NEED_SERVICE_RESTART = True
        print(
            "Changes only take effect after selecting 'Apply Changes' in the dashboard!"
        )
        prompt_clear_screen()
    dashboard()


def access_controls_menu():
    global NEED_SERVICE_RESTART

    title = "Select any option:"
    options = [
        "Unblock Porn" if is_porn_blocked() else "Block Porn",
        "Back to Main Menu",
    ]
    option, _ = pick(options, title)
    if option == "Block Porn":
        NEED_SERVICE_RESTART = True
        run_system_cmd([f"{os.getcwd()}/lib/shell/access_control/block_porn.sh"])
        enable_porn_dns_blocking(BLOCKY_CONFIG_FILE)
        sleep(1)
        clear_screen()
        access_controls_menu()
    elif option == "Unblock Porn":
        NEED_SERVICE_RESTART = True
        run_system_cmd([f"{os.getcwd()}/lib/shell/access_control/unblock_porn.sh"])
        disable_porn_dns_blocking(BLOCKY_CONFIG_FILE)
        sleep(1)
        clear_screen()
        access_controls_menu()
    dashboard()


def user_info_menu(username: str):
    global NEED_SERVICE_RESTART

    title = f"Select any option for {username}:"
    options = [
        "View QR codes and share URLs",
        "Reset Credentials",
        "Remove User",
        "Back to Users Management Menu",
    ]
    option, _ = pick(options, title)
    if option == "View QR codes and share URLs":
        print_client_info(username, RAINB0W_USERS_FILE, RAINB0W_CONFIG_FILE)
        prompt_clear_screen()
    elif option == "Reset Credentials":
        title = f"Confirm resetting credentials for '{username}'?"
        options = ["Yes", "No"]
        option, _ = pick(options, title)
        if option == "Yes":
            rainb0w_users = get_users(RAINB0W_USERS_FILE)
            if rainb0w_users:
                for user in rainb0w_users:
                    if user["name"] == username:
                        reset_user_credentials(username, RAINB0W_USERS_FILE)
                        gen_user_links_qrcodes(user, RAINB0W_CONFIG_FILE)
                        print(
                            "Credentials reset. You can view the new links and QR codes already but changes only take effect after selecting 'Apply Changes' in the dashboard!"
                        )
                        prompt_clear_screen()
                        NEED_SERVICE_RESTART = True
    elif option == "Remove User":
        title = f"Confirm removing '{username}'?"
        options = ["Yes", "No"]
        option, _ = pick(options, title)
        if option == "Yes":
            NEED_SERVICE_RESTART = True
            remove_user(
                username,
                RAINB0W_CONFIG_FILE,
                RAINB0W_USERS_FILE,
                XRAY_CONFIG_FILE,
                HYSTERIA_CONFIG_FILE,
            )
            clear_screen()
        else:
            user_info_menu(username)


def users_management_menu():
    global NEED_SERVICE_RESTART

    title = "Select any option:"
    options = [
        "Add a New User",
        "Back to Main Menu",
    ]
    # If we have existing users, display a numbered list of them in the menu
    usernames: List[str] = []
    users = get_users(RAINB0W_USERS_FILE)
    if users:
        for idx, user in enumerate(users):
            usernames.append(f"{idx}. {user['name']}")
        options[:0] = usernames
        title = "Add or remove a user:"
    option, _ = pick(options, title)
    if option == "Add a New User":
        username_input = input("Enter a name for the new user: ")
        if username_input:
            if any(user["name"] == username_input for user in users):
                print(f"A user with the given name '{username_input}' already exists!")
                prompt_clear_screen()
            else:
                NEED_SERVICE_RESTART = True
                user_info = create_new_user(username_input)
                rainb0w_users = get_users(RAINB0W_USERS_FILE)
                rainb0w_users.append(user_info)
                save_users(rainb0w_users, RAINB0W_USERS_FILE)
                add_user_to_proxies(
                    user_info,
                    RAINB0W_CONFIG_FILE,
                    XRAY_CONFIG_FILE,
                    HYSTERIA_CONFIG_FILE,
                )
                print(
                    "Changes only take effect after selecting 'Apply Changes' in the dashboard!"
                )
                prompt_clear_screen()
        users_management_menu()
    elif option in usernames:
        user = re.sub(r"^.*?\.\s*", "", str(option))
        user_info_menu(user)
        users_management_menu()
    elif option == "Back to Main Menu":
        dashboard()
    dashboard()


def backup():
    print(
        f"Backing up users and config files to [bold blue]'{RAINB0W_BACKUP_DIR}'[/bold blue]"
    )
    if not os.path.exists(RAINB0W_BACKUP_DIR):
        os.makedirs(RAINB0W_BACKUP_DIR)
    copy_file(RAINB0W_CONFIG_FILE, RAINB0W_BACKUP_DIR)
    copy_file(RAINB0W_USERS_FILE, RAINB0W_BACKUP_DIR)
    copy_dir(CLIENT_CONFIG_FILES_DIR, RAINB0W_BACKUP_DIR)

    print("[bold green]Backup finished successfully.")
    prompt_clear_screen()
    dashboard()


def uninstall():
    title = """
Proceeding will stop and remove all Docker containers, volumes, networks and
revert all changes made to the system such as firewall settings and kernel tweaks!
Make sure you have made a backup of your configuration and users
if you'd like to restore them later on.

Do you confirm?
"""
    options = ["CANCEL", "OKAY"]
    option, _ = pick(options, title)
    if option == "OKAY":
        run_system_cmd([f"{os.getcwd()}/lib/shell/uninstall.sh"])
        prompt_clear_screen()
        exit(0)
    else:
        dashboard()


def update():
    title = """
IMPORTANT: Proceeding will pull the latest Docker images of proxies and
update them on your system, BUT doing so without upgrading your CLIENT apps first
may cause connectivity issues, and you won't be able to connect until you upgrade your clients!
Please update your client apps first and then proceed here.

Do you want to continue?
"""
    options = ["CANCEL", "OKAY"]
    option, _ = pick(options, title)
    if option == "OKAY":
        run_system_cmd([f"{os.getcwd()}/lib/shell/update.sh"])
    else:
        dashboard()


def dashboard():
    global NEED_SERVICE_RESTART
    title = """Choose any options to proceed:"""
    options = [
        "SNI Settings",
        "Performance Settings",
        # "MTProto Settings",
        "Access Controls",
        "Manage Users",
        "Backup",
        "Uninstall",
        "Update",
        "Apply Changes" if NEED_SERVICE_RESTART else "Exit",
    ]
    option, _ = pick(options, title)
    if option == "SNI Settings":
        sni_menu()
    elif option == "Performance Settings":
        performance_menu()
    elif option == "MTProto Settings":
        mtproto_menu()
    elif option == "Access Controls":
        access_controls_menu()
    elif option == "Manage Users":
        users_management_menu()
    elif option == "Backup":
        backup()
    elif option == "Uninstall":
        uninstall()
    elif option == "Update":
        update()
    elif option == "Apply Changes":
        clear_screen()
        print("Applying Changes!")
        # We let the parent bash process handle the rest
        exit(1)
    elif option == "Exit":
        print("Exiting!")
        exit(0)

def signal_handler(sig, frame):
    print("\nOkay! Exiting!")
    sys.exit(1)

if __name__ == "__main__":
    # Enable bailing out!
    signal.signal(signal.SIGINT, signal_handler)
    dashboard()
