#!/usr/bin/env python3

import os
import signal
import sys

from base.config import (
    CLIENT_CONFIG_FILES_DIR,
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
from user.user_manager import add_user_to_proxies, create_new_user, prompt_username
from utils.cert_utils import prompt_fake_sni, prompt_organization_name
from utils.helper import copy_dir, copy_file, load_toml, progress_indicator, save_toml
from utils.net_utils import prompt_port_number


def apply_config(username=None):
    rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)
    rainb0w_users = load_toml(RAINB0W_USERS_FILE)

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

    # If this is a new Express/Custom deployment, we need to create a default user
    # if it's a 'Restore' we will restore the existing users one by one
    if username:
        add_user_to_proxies(
            create_new_user(username),
            RAINB0W_USERS_FILE,
            RAINB0W_CONFIG_FILE,
            XRAY_CONFIG_FILE,
            HYSTERIA_CONFIG_FILE,
        )
    else:
        # Add users from the rainb0w_users.toml into proxies
        for user in rainb0w_users["users"]:
            add_user_to_proxies(
                user,
                RAINB0W_USERS_FILE,
                RAINB0W_CONFIG_FILE,
                XRAY_CONFIG_FILE,
                HYSTERIA_CONFIG_FILE,
            )

    exit(0)


def restore_config():
    if os.path.exists(RAINB0W_BACKUP_DIR):
        copy_file(
            f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_CONFIG_FILE)}",
            RAINB0W_CONFIG_FILE,
        )
        copy_file(
            f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_USERS_FILE)}",
            RAINB0W_USERS_FILE,
        )
        copy_dir(f"{RAINB0W_BACKUP_DIR}/clients", CLIENT_CONFIG_FILES_DIR)
        print("Restoring your configuration and users...")
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

    progress_indicator(1, 8, "Fake SNI")
    rainb0w_config["CERT"]["FAKE_SNI"] = prompt_fake_sni()

    progress_indicator(2, 8, "Organization Name")
    rainb0w_config["CERT"]["ORGANIZATION"] = prompt_organization_name()

    progress_indicator(3, 8, "REALITY Port")
    rainb0w_config["REALITY"]["PORT"], tcp_ports = prompt_port_number(
        "REALITY", "TCP", tcp_ports
    )

    progress_indicator(4, 8, "MTProto Port")
    rainb0w_config["MTPROTO"]["PORT"], tcp_ports = prompt_port_number(
        "MTProto", "TCP", tcp_ports
    )

    progress_indicator(5, 8, "Hysteria Port")
    rainb0w_config["HYSTERIA"]["PORT"], udp_ports = prompt_port_number(
        "Hysteria", "UDP", udp_ports
    )

    progress_indicator(6, 8, "Hysteria Obfuscation")
    obfs = prompt_hysteria_obfs()
    if obfs:
        rainb0w_config["HYSTERIA"]["OBFS"] = obfs

    progress_indicator(7, 8, "Hysteria ALPN")
    alpn = prompt_hysteria_alpn()
    if alpn:
        rainb0w_config["HYSTERIA"]["ALPN"] = alpn

    # Finally prompt for a username
    progress_indicator(8, 8, "User Management")
    username = prompt_username()

    # Save the configuration to file because we're going to pass it around next
    save_toml(rainb0w_config, RAINB0W_CONFIG_FILE)

    apply_config(username=username)


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
