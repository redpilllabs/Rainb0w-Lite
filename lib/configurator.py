#!/usr/bin/env python3

import os
import signal
import sys

from base.config import (
    HYSTERIA_CONFIG_FILE,
    HYSTERIA_DOCKER_COMPOSE_FILE,
    MTPROTOPY_CONFIG_FILE,
    MTPROTOPY_DOCKER_COMPOSE_FILE,
    RAINB0W_BACKUP_DIR,
    RAINB0W_CONFIG_FILE,
    RAINB0W_USERS_FILE,
    XRAY_CONFIG_FILE,
    XRAY_DOCKER_COMPOSE_FILE,
)
from proxy.hysteria import (
    configure_hysteria,
    prompt_hysteria_alpn,
    prompt_hysteria_obfs,
)
from proxy.mtproto import configure_mtproto
from proxy.xray import configure_xray_reality
from user.user_manager import (
    add_user_to_proxies,
    create_new_user,
    get_users,
    prompt_username,
    save_users,
)
from utils.cert_utils import prompt_fake_sni
from utils.helper import copy_file, load_toml, progress_indicator, save_toml
from utils.net_utils import prompt_port_number


def apply_config():
    rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)

    configure_xray_reality(
        rainb0w_config["REALITY"],
        rainb0w_config["CERT"],
        XRAY_CONFIG_FILE,
        XRAY_DOCKER_COMPOSE_FILE,
    )

    configure_hysteria(
        rainb0w_config["HYSTERIA"],
        HYSTERIA_CONFIG_FILE,
        HYSTERIA_DOCKER_COMPOSE_FILE,
    )

    configure_mtproto(
        rainb0w_config["MTPROTO"],
        rainb0w_config["CERT"],
        MTPROTOPY_CONFIG_FILE,
        MTPROTOPY_DOCKER_COMPOSE_FILE,
    )

    # Add users from the rainb0w_users.toml into proxies
    rainb0w_users = get_users(RAINB0W_USERS_FILE)
    for user in rainb0w_users:
        add_user_to_proxies(
            user,
            RAINB0W_CONFIG_FILE,
            XRAY_CONFIG_FILE,
            HYSTERIA_CONFIG_FILE,
        )

    exit(0)


def restore_config():
    print("Restoring your configuration and users...")
    if os.path.exists(RAINB0W_BACKUP_DIR):
        copy_file(
            f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_CONFIG_FILE)}",
            RAINB0W_CONFIG_FILE,
        )
        copy_file(
            f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_USERS_FILE)}",
            RAINB0W_USERS_FILE,
        )
        apply_config()
    else:
        print(f"ERROR: No data found at: {RAINB0W_BACKUP_DIR}")
        print(
            f"Please copy your backup files to \
                    '{RAINB0W_BACKUP_DIR}' and run the installer again!"
        )
        exit(1)


def configure():
    rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)
    tcp_ports = set()
    udp_ports = set()

    progress_indicator(1, 7, "Fake SNI")
    rainb0w_config["CERT"]["FAKE_SNI"] = prompt_fake_sni()

    progress_indicator(2, 7, "REALITY Port")
    rainb0w_config["REALITY"]["PORT"], tcp_ports = prompt_port_number(
        "REALITY", "TCP", tcp_ports
    )

    progress_indicator(3, 7, "MTProto Port")
    rainb0w_config["MTPROTO"]["PORT"], tcp_ports = prompt_port_number(
        "MTProto", "TCP", tcp_ports
    )

    progress_indicator(4, 7, "Hysteria Port")
    rainb0w_config["HYSTERIA"]["PORT"], udp_ports = prompt_port_number(
        "Hysteria", "UDP", udp_ports
    )

    progress_indicator(5, 7, "Hysteria Obfuscation")
    obfs = prompt_hysteria_obfs()
    if obfs:
        rainb0w_config["HYSTERIA"]["OBFS"] = obfs

    progress_indicator(6, 7, "Hysteria ALPN")
    alpn = prompt_hysteria_alpn()
    if alpn:
        rainb0w_config["HYSTERIA"]["ALPN"] = alpn

    # Finally prompt for a username
    progress_indicator(7, 7, "User Management")
    username = prompt_username()

    # Generate a user object with the given name and save it to users file
    user_info = create_new_user(username)
    rainb0w_users = get_users(RAINB0W_USERS_FILE)
    rainb0w_users.append(user_info)
    save_users(rainb0w_users, RAINB0W_USERS_FILE)

    # Save the configuration to file because we're going to pass it around next
    save_toml(rainb0w_config, RAINB0W_CONFIG_FILE)

    apply_config()


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "Install":
            configure()
        elif sys.argv[1] == "Restore":
            restore_config()
        else:
            print("Unknown installation type passed! Exiting!")
            exit(1)
    else:
        print("Not enough args passed! Exiting!")
        exit(1)


def signal_handler(sig, frame):
    print("\nOkay! Exiting!")
    sys.exit(1)


if __name__ == "__main__":
    # Enable bailing out!
    signal.signal(signal.SIGINT, signal_handler)
    main()
