#!/usr/bin/env python3

import os
import random
import signal
import sys

from base.config import (
    HYSTERIA_CONFIG_FILE,
    MTPROTOPY_CONFIG_FILE,
    RAINB0W_BACKUP_DIR,
    RAINB0W_CONFIG_FILE,
    RAINB0W_HOME_DIR,
    RAINB0W_USERS_FILE,
    XRAY_CONFIG_FILE,
)
from pick import pick
from proxy.hysteria import configure_hysteria
from proxy.mtproto import (
    change_mtproto_adtag,
    configure_mtproto,
    prompt_extra_port_number,
    prompt_mtproto_adtag,
)
from proxy.xray import configure_xray_reality
from user.user_manager import (
    add_user_to_proxies,
    create_new_user,
    get_users,
    prompt_username,
    save_users,
)
from utils.cert_utils import prompt_fake_sni
from utils.helper import (
    copy_file,
    gen_random_string,
    load_toml,
    progress_indicator,
    remove_dir,
    save_toml,
)


def apply_config():
    rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)

    if rainb0w_config["XRAY"]["IS_ENABLED"]:
        configure_xray_reality(
            rainb0w_config["XRAY"],
            rainb0w_config["CERT"],
            XRAY_CONFIG_FILE,
        )

    if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
        configure_hysteria(
            rainb0w_config["HYSTERIA"],
            HYSTERIA_CONFIG_FILE,
        )

    if rainb0w_config["MTPROTO"]["IS_ENABLED"]:
        configure_mtproto(
            rainb0w_config["MTPROTO"],
            rainb0w_config["CERT"],
            MTPROTOPY_CONFIG_FILE,
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

    title = "Select the proxies you'd like to deploy [Press 'Space' to mark]:"
    options = ["Xray REALITY", "MTProto", "Hysteria"]

    selected = pick(options, title, multiselect=True, min_selection_count=1)
    selected = [item[0] for item in selected]  # type: ignore

    # We need 2 steps regardless of proxy choice,
    #  one for the fake sni and one for username prompt
    total_steps = 2

    # Hysteria requires two more steps (ALPN and obfs)
    if "Hysteria" in selected:
        total_steps += 1
    # MTProto adtag prompt
    if "MTProto" in selected:
        total_steps += 1
        # MTProto extra port prompt
        if "Xray REALITY" in selected:
            total_steps += 1

    if "Xray REALITY" not in selected and "Hysteria" not in selected:
        rainb0w_config["BLOCKY"]["IS_ENABLED"] = False
        remove_dir(f"{RAINB0W_HOME_DIR}/blocky")
    else:
        rainb0w_config["BLOCKY"]["IS_ENABLED"] = True

    curr_step = 1

    progress_indicator(curr_step, total_steps, "Fake SNI")
    rainb0w_config["CERT"]["FAKE_SNI"] = prompt_fake_sni()
    curr_step += 1

    if "Xray REALITY" in selected:
        rainb0w_config["XRAY"]["IS_ENABLED"] = True
    else:
        remove_dir(f"{RAINB0W_HOME_DIR}/xray")

    if "MTProto" in selected:
        rainb0w_config["MTPROTO"]["IS_ENABLED"] = True
        if "Xray REALITY" in selected:
            progress_indicator(curr_step, total_steps, "MTProto Extra Port")
            rainb0w_config["MTPROTO"]["EXTRA_PORT"] = prompt_extra_port_number(
                "MTProto", "TCP"
            )
            curr_step += 1
        else:
            rainb0w_config["MTPROTO"]["EXTRA_PORT"] = 443

        progress_indicator(curr_step, total_steps, "MTProto AdTag")
        adtag = prompt_mtproto_adtag()
        change_mtproto_adtag(RAINB0W_CONFIG_FILE, MTPROTOPY_CONFIG_FILE, adtag)
        curr_step += 1
    else:
        remove_dir(f"{RAINB0W_HOME_DIR}/mtproto")

    if "Hysteria" in selected:
        progress_indicator(curr_step, total_steps, "Hysteria Mode")
        title = "Select Hysteria running mode:"
        options = ["Raw Obfuscated UDP [Recommended]", "Normal QUIC"]

        option, _ = pick(options, title)
        if option == "Raw Obfuscated UDP [Recommended]":
            # Port will be set to 8443
            rainb0w_config["HYSTERIA"]["OBFS"] = gen_random_string(
                random.randint(8, 12)
            )
        elif option == "Normal QUIC":
            # Port will be set to 443/udp
            rainb0w_config["HYSTERIA"]["ALPN"] = "h3"

        rainb0w_config["HYSTERIA"]["IS_ENABLED"] = True
        curr_step += 1
    else:
        remove_dir(f"{RAINB0W_HOME_DIR}/hysteria")

    # Finally prompt for a username
    progress_indicator(curr_step, total_steps, "User Management")
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
