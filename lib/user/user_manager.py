import base64
import os
import random
from os import urandom
from random import randint
from uuid import uuid4

from base.config import CLIENT_CONFIG_FILES_DIR, PUBLIC_IP
from proxy.hysteria import (
    configure_hysteria_client,
    hysteria_add_user,
    hysteria_remove_user,
)
from proxy.mtproto import configure_mtproto_client
from proxy.xray import configure_xray_reality_client, xray_add_user, xray_remove_user
from rich import print
from utils.helper import (
    bytes_to_raw_str,
    gen_qrcode,
    gen_random_string,
    load_toml,
    load_txt_file,
    print_txt_file,
    remove_dir,
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
    print(f"Adding '{username}' as a new user...")
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


def add_user_to_proxies(
    user_info: dict,
    rainb0w_users_file: str,
    rainb0w_config_file: str,
    xray_config_file: str,
    hysteria_config_file: str,
):
    rainb0w_config = load_toml(rainb0w_config_file)

    if not os.path.exists(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}"):
        os.makedirs(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}")

    # Add user to proxies (MTProto is directly loaded from the users.toml file)
    xray_add_user(user_info, xray_config_file)
    hysteria_add_user(user_info, hysteria_config_file)

    # Create a client json file for applicable proxies
    if not os.path.exists(CLIENT_CONFIG_FILES_DIR):
        os.makedirs(CLIENT_CONFIG_FILES_DIR)
    configure_xray_reality_client(
        user_info, rainb0w_config["REALITY"], rainb0w_config["CERT"]
    )
    save_qrcode(
        load_txt_file(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/reality-url.txt"),
        f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/reality-qrcode.png",
    )
    configure_hysteria_client(
        user_info, rainb0w_config["HYSTERIA"], rainb0w_config["CERT"]
    )
    save_qrcode(
        load_txt_file(
            f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria-url.txt"
        ),
        f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria-qrcode.png",
    )
    configure_mtproto_client(
        user_info,
        rainb0w_config["MTPROTO"],
        rainb0w_config["CERT"],
        base64_encode=False,
    )
    save_qrcode(
        load_txt_file(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/mtproto-url.txt"),
        f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/mtproto-qrcode.png",
    )

    rainb0w_users = get_users(rainb0w_users_file)
    rainb0w_users.append(user_info)
    save_users(rainb0w_users, rainb0w_users_file)


def remove_user(
    username: str,
    rainb0w_users_file: str,
    xray_config_file: str,
    hysteria_config_file: str,
):
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print(f"Removing the user '{username}'...")
                xray_remove_user(user, xray_config_file)
                hysteria_remove_user(user, hysteria_config_file)
                remove_dir(f"{CLIENT_CONFIG_FILES_DIR}/{user['name']}")
                rainb0w_users.remove(user)

        save_users(rainb0w_users, rainb0w_users_file)


def print_client_info(username: str, rainb0w_users_file: str, rainb0w_config_file: str):
    rainb0w_config = load_toml(rainb0w_config_file)
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print("=" * 60)
                print("\n*********************** Xray REALITY ***********************")
                print_txt_file(f"{CLIENT_CONFIG_FILES_DIR}/{username}/reality-url.txt")
                gen_qrcode(
                    load_txt_file(
                        f"{CLIENT_CONFIG_FILES_DIR}/{username}/reality-url.txt"
                    )
                )
                print("\n*********************** MTProto ***********************")
                print_txt_file(f"{CLIENT_CONFIG_FILES_DIR}/{username}/mtproto-url.txt")
                gen_qrcode(
                    load_txt_file(
                        f"{CLIENT_CONFIG_FILES_DIR}/{username}/mtproto-url.txt"
                    )
                )
                print("\n*********************** Hysteria ***********************")
                print_txt_file(f"{CLIENT_CONFIG_FILES_DIR}/{username}/hysteria-url.txt")
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
    SNI:                {rainb0w_config['HYSTERIA']['FAKE_SNI']}
    ALPN:               {rainb0w_config['HYSTERIA']['ALPN']}
    Obfuscation:        {rainb0w_config['HYSTERIA']['OBFS']}
    Auth. Type:         BASE64
    Payload:            {bytes_to_raw_str(base64.b64encode(user["password"].encode()))}
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
You can also find pre-configured client.json files for {user['name']} at
Xray REALITY:   [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/reality.json[/green]
Hysteria:       [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/hysteria.json[/green]

You can also find these QRCodes and pre-configured client.json files for '${username}' at
Xray REALITY:
    - JSON:   [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/reality.json[/green]
    - QRCODE: [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/reality-qrcode.png[/green]
Hysteria:
    - JSON:   [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/hysteria.json[/green]
    - QRCODE: [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}/hysteria-qrcode.png[/green]
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
