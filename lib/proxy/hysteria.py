
from base.config import CLIENT_CONFIG_FILES_DIR, HYSTERIA_CLIENT_TEMPLATE_CONFIG_FILE
from utils.helper import gen_random_string, load_yaml, save_yaml, write_txt_file


def configure_hysteria(
    proxy_config: dict,
    hysteria_config_file: str,
):
    print("Configuring Hysteria...")
    hysteria_config = load_yaml(hysteria_config_file)

    hysteria_config["masquerade"]["proxy"]["url"] = f"https://{proxy_config['SNI']}"
    if proxy_config["OBFS"]:
        hysteria_config['obfs'] = {'type': 'salamander', 'salamander': {'password': proxy_config["OBFS"]}}

    save_yaml(hysteria_config, hysteria_config_file)


def hysteria_add_user(user_info: dict, hysteria_config_file: str):
    hysteria_config = load_yaml(hysteria_config_file)
    if hysteria_config['auth']['userpass']:
        hysteria_config['auth']['userpass'][user_info["name"]] = user_info["password"]
    else:
        hysteria_config['auth']['userpass'] = {user_info["name"]: user_info["password"]}

    save_yaml(hysteria_config, hysteria_config_file)


def hysteria_remove_user(user_info: dict, hysteria_config_file: str):
    hysteria_config = load_yaml(hysteria_config_file)
    user_found = hysteria_config["auth"]['userpass'].get(user_info["name"])
    if user_found:
        del hysteria_config["auth"]['userpass'][user_info["name"]]

    save_yaml(hysteria_config, hysteria_config_file)


def configure_hysteria_client(user_info: dict, proxy_config: dict):
    from base.config import PUBLIC_IP

    client_config = load_yaml(HYSTERIA_CLIENT_TEMPLATE_CONFIG_FILE)

    client_config["server"] = client_config["server"].replace("USERNAME", user_info["name"])
    client_config["server"] = client_config["server"].replace("PASSWORD", user_info["password"])
    client_config["server"] = client_config["server"].replace("YOUR_SNI", proxy_config["SNI"])

    if proxy_config["OBFS"]:
        client_config["server"] = client_config["server"].replace("PUBLIC_IP", f"{PUBLIC_IP}:8443")
        client_config["server"] +=  "&obfs=salamander"
        client_config["server"] +=  f"&obfs-password={proxy_config['OBFS']}"
    else:
        client_config["server"] = client_config["server"].replace("PUBLIC_IP", f"{PUBLIC_IP}")

    save_yaml(
        client_config, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria.yml"
    )

    if {proxy_config["OBFS"]}:
        share_url =f"hysteria2://{user_info['name']}:{user_info['password']}@{PUBLIC_IP}:8443/?insecure=1&obfs=salamander&obfs-password={proxy_config['OBFS']}&sni={proxy_config['SNI']}#{user_info['name']}%20Hysteria"
    else:
        share_url =f"hysteria2://{user_info['name']}:{user_info['password']}@{PUBLIC_IP}:8443/?insecure=1&sni={proxy_config['SNI']}#{user_info['name']}%20Hysteria"

    write_txt_file(
        share_url, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria-url.txt"
    )
