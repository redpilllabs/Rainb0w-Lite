import os
import random
from os import urandom
from random import randint
from uuid import uuid4

from rich import print

from base.config import CLIENT_CONFIG_FILES_DIR, PUBLIC_IP
from proxy.hysteria import (
    configure_hysteria_client,
    hysteria_add_user,
    hysteria_remove_user,
)
from proxy.mtproto import configure_mtproto_client
from proxy.xray import configure_xray_reality_client, xray_add_user, xray_remove_user
from utils.helper import (
    gen_qrcode,
    gen_random_string,
    load_json,
    load_toml,
    load_txt_file,
    print_txt_file,
    remove_dir,
    save_json,
    save_qrcode,
    save_toml,
)


def get_users(rainb0w_users_file: str) -> list:
    rainb0w_users = load_toml(rainb0w_users_file)
    if "users" in rainb0w_users:
        return rainb0w_users["users"]
    else:
        rainb0w_users["users"] = []
        return rainb0w_users["users"]


def save_users(users: list, users_toml_file: str):
    """
    This is just a wrapper function to be consistent with 'get_users'
    """
    save_toml({"users": users}, users_toml_file)


def create_new_user(username: str):
    password = gen_random_string(randint(8, 12))
    uuid = str(uuid4())
    short_id = "".join(random.choice("0123456789abcdef") for _ in range(8))
    secret = urandom(16).hex()

    user_info = {
        "name": username,
        "password": password,
        "uuid": uuid,
        "secret": secret,
        "short_id": short_id,
    }
    return user_info


def gen_user_links_qrcodes(
    user_info: dict,
    rainb0w_config_file: str,
):
    """
    Generates share links and QR codes with the given user info and proxy configuration

    Args:
        user_info (dict): User dictionary containing username, secrets and passwords
        rainb0w_config_file (str): Path to the rainb0w_config.toml file holding proxy configuration
    """
    rainb0w_config = load_toml(rainb0w_config_file)

    if not os.path.exists(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}"):
        os.makedirs(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}")

    if rainb0w_config["XRAY"]["IS_ENABLED"]:
        configure_xray_reality_client(user_info, rainb0w_config["XRAY"])
        save_qrcode(
            load_txt_file(
                f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/reality-url.txt"
            ),
            f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/reality-qrcode.png",
        )

    if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
        configure_hysteria_client(user_info, rainb0w_config["HYSTERIA"])
        save_qrcode(
            load_txt_file(
                f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria-url.txt"
            ),
            f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria-qrcode.png",
        )

    if rainb0w_config["MTPROTO"]["IS_ENABLED"]:
        configure_mtproto_client(
            user_info,
            rainb0w_config["MTPROTO"],
            base64_encode=False,
        )
        save_qrcode(
            load_txt_file(
                f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/mtproto-url.txt"
            ),
            f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/mtproto-qrcode.png",
        )


def add_user_to_proxies(
    user_info: dict,
    rainb0w_config_file: str,
    xray_config_file: str,
    hysteria_config_file: str,
):
    print(f"Adding user [green]'{user_info['name']}'[/green] to proxies")
    rainb0w_config = load_toml(rainb0w_config_file)

    if rainb0w_config["XRAY"]["IS_ENABLED"]:
        xray_add_user(user_info, xray_config_file)
    if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
        hysteria_add_user(user_info, hysteria_config_file)

    # MTProto users are directly loaded from the users.toml file

    # Generate user sharing links and QR codes
    gen_user_links_qrcodes(user_info, rainb0w_config_file)


def remove_user(
    username: str,
    rainb0w_config_file: str,
    rainb0w_users_file: str,
    xray_config_file: str,
    hysteria_config_file: str,
):
    rainb0w_config = load_toml(rainb0w_config_file)
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print(f"Removing the user '{username}'...")
                if rainb0w_config["XRAY"]["IS_ENABLED"]:
                    xray_remove_user(user, xray_config_file)
                if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
                    hysteria_remove_user(user, hysteria_config_file)
                remove_dir(f"{CLIENT_CONFIG_FILES_DIR}/{user['name']}")
                rainb0w_users.remove(user)
                save_users(rainb0w_users, rainb0w_users_file)


def reset_user_credentials(
    username: str,
    rainb0w_users_file: str,
    rainb0w_config_file: str,
    xray_config_file: str,
    hysteria_config_file: str,
):
    rainb0w_users = get_users(rainb0w_users_file)
    rainb0w_config = load_toml(rainb0w_config_file)
    xray_config = load_json(xray_config_file)
    hysteria_config = load_json(hysteria_config_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print(
                    f"Resetting UUID, shortID, password, and secrets for '{username}'..."
                )
                new_password = gen_random_string(randint(8, 12))
                new_uuid = str(uuid4())
                new_short_id = "".join(
                    random.choice("0123456789abcdef") for _ in range(8)
                )
                new_secret = urandom(16).hex()

                if rainb0w_config["XRAY"]["IS_ENABLED"]:
                    for client in xray_config["inbounds"][0]["settings"]["clients"]:
                        if "id" in client:
                            if client["id"] == user["uuid"]:
                                client["id"] = new_uuid

                    xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
                        "shortIds"
                    ] = [
                        new_short_id if item == user["short_id"] else item
                        for item in xray_config["inbounds"][0]["streamSettings"][
                            "realitySettings"
                        ]["shortIds"]
                    ]

                if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
                    hysteria_config["auth"]["config"] = [
                        new_password if item == user["password"] else item
                        for item in hysteria_config["auth"]["config"]
                    ]

                user["password"] = new_password
                user["uuid"] = new_uuid
                user["short_id"] = new_short_id
                user["secret"] = new_secret
                save_users(rainb0w_users, rainb0w_users_file)
                save_json(xray_config, xray_config_file)
                save_json(hysteria_config, hysteria_config_file)


def print_client_info(username: str, rainb0w_users_file: str, rainb0w_config_file: str):
    rainb0w_config = load_toml(rainb0w_config_file)
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print("=" * 60)
                if rainb0w_config["XRAY"]["IS_ENABLED"]:
                    print(
                        "\n*********************** Xray REALITY ***********************"
                    )
                    print_txt_file(
                        f"{CLIENT_CONFIG_FILES_DIR}/{username}/reality-url.txt"
                    )
                    gen_qrcode(
                        load_txt_file(
                            f"{CLIENT_CONFIG_FILES_DIR}/{username}/reality-url.txt"
                        )
                    )
                if rainb0w_config["MTPROTO"]["IS_ENABLED"]:
                    print("\n*********************** MTProto ***********************")
                    print_txt_file(
                        f"{CLIENT_CONFIG_FILES_DIR}/{username}/mtproto-url.txt"
                    )
                    gen_qrcode(
                        load_txt_file(
                            f"{CLIENT_CONFIG_FILES_DIR}/{username}/mtproto-url.txt"
                        )
                    )
                if rainb0w_config["HYSTERIA"]["IS_ENABLED"]:
                    print("\n*********************** Hysteria ***********************")
                    print_txt_file(
                        f"{CLIENT_CONFIG_FILES_DIR}/{username}/hysteria-url.txt"
                    )
                    gen_qrcode(
                        load_txt_file(
                            f"{CLIENT_CONFIG_FILES_DIR}/{username}/hysteria-url.txt"
                        )
                    )
                    print(
                        f"""
If your client does not support share links, configure it as the following:

Server:             {PUBLIC_IP}
Port:               {rainb0w_config['HYSTERIA']['PORT']}
Protocol:           UDP
SNI:                {rainb0w_config['HYSTERIA']['SNI']}
ALPN:               {rainb0w_config['HYSTERIA']['ALPN']}
Obfuscation:        {rainb0w_config['HYSTERIA']['OBFS']}
Auth. Type:         STRING
Payload:            {user["password"]}
Allow Insecure:     Enabled
Max Upload:         YOUR REAL UPLOAD SPEED
Max Download:       YOUR REAL DOWNLOAD SPEED
QUIC Stream:        1677768
QUIC Conn.:         4194304
Disable Path MTU Discovery: Enabled
            """
                    )
                print("=" * 60)
                print(
                    f"""\n
You can also find these QRCodes and pre-configured client.json files for '{username}' at
[green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/[/green]

You can use FTP clients, scp command, or even 'cat' them on the terminal and
then copy and paste to a local json file to provide to your client apps.

[bold yellow]NOTE: DO NOT SHARE THESE LINKS AND INFORMATION OVER SMS OR DOMESTIC MESSENGERS,
USE EMAILS OR OTHER SECURE WAYS OF COMMUNICATION INSTEAD![/bold yellow]
                """.lstrip()
                )


def prompt_username():
    username = input("\nEnter a username for your first user: ")
    while not username or not username.isascii():
        print("\nInvalid username!")
        username = input("Enter a username for your first user: ")

    return username
