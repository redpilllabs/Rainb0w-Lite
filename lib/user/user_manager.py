import os
import random
from os import urandom
from random import randint
from uuid import uuid4

from base.config import CLIENT_CONFIG_FILES_DIR
from proxy.hysteria import (
    configure_hysteria_client,
    hysteria_add_user,
    hysteria_remove_user,
    print_hysteria_client_info,
)
from proxy.mtproto import print_mtproto_share_links
from proxy.xray import (
    configure_xray_reality_client,
    print_reality_share_link,
    xray_add_user,
    xray_remove_user,
)
from rich import print
from utils.helper import (
    gen_random_string,
    load_toml,
    print_txt_file,
    remove_file,
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

    # Add user to proxies (MTProto is directly loaded from the users.toml file)
    xray_add_user(user_info, xray_config_file)
    hysteria_add_user(user_info, hysteria_config_file)

    # Create a client json file for applicable proxies
    if not os.path.exists(CLIENT_CONFIG_FILES_DIR):
        os.makedirs(CLIENT_CONFIG_FILES_DIR)
    configure_xray_reality_client(
        user_info, rainb0w_config["REALITY"], rainb0w_config["CERT"]
    )
    configure_hysteria_client(
        user_info, rainb0w_config["HYSTERIA"], rainb0w_config["CERT"]
    )

    with open(f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}.txt", "w") as file:
        file.write(
            print_reality_share_link(
                user_info, rainb0w_config["REALITY"], rainb0w_config["CERT"]
            )
        )
        file.write(
            print_mtproto_share_links(
                user_info, rainb0w_config["MTPROTO"], rainb0w_config["CERT"]
            )
        )
        file.write(
            print_hysteria_client_info(
                user_info, rainb0w_config["HYSTERIA"], rainb0w_config["CERT"]
            )
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
                remove_file(f"{CLIENT_CONFIG_FILES_DIR}/{user['name']}-reality.json")
                remove_file(f"{CLIENT_CONFIG_FILES_DIR}/{user['name']}-hysteria.json")
                rainb0w_users.remove(user)

        save_users(rainb0w_users, rainb0w_users_file)


def print_client_info(username: str, rainb0w_users_file: str):
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print("=" * 60)
                print_txt_file(f"{CLIENT_CONFIG_FILES_DIR}/{user['name']}.txt")
                print("=" * 60)
            print(
                f"""\n
You can also find pre-configured client.json files for {user['name']} at
Xray REALITY:   [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}-reality.json[/green]
Hysteria:       [green]{CLIENT_CONFIG_FILES_DIR}/{user['name']}-hysteria.json[/green]
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
