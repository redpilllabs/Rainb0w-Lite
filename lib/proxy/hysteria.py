
from base.config import CLIENT_CONFIG_FILES_DIR, HYSTERIA_CLIENT_TEMPLATE_CONFIG_FILE
from utils.helper import load_json, save_json, write_txt_file


def configure_hysteria(
    proxy_config: dict,
    hysteria_config_file: str,
):
    print("Configuring Hysteria...")
    hysteria_config = load_json(hysteria_config_file)

    hysteria_config["listen"] = f":{proxy_config['PORT']}"
    if proxy_config["OBFS"]:
        hysteria_config["obfs"] = proxy_config["OBFS"]
    if proxy_config["ALPN"]:
        hysteria_config["alpn"] = proxy_config["ALPN"]

    save_json(hysteria_config, hysteria_config_file)


def hysteria_add_user(user_info: dict, hysteria_config_file: str):
    hysteria_config = load_json(hysteria_config_file)
    hysteria_config["auth"]["config"].append(user_info["password"])

    save_json(hysteria_config, hysteria_config_file)


def hysteria_remove_user(user_info: dict, hysteria_config_file: str):
    hysteria_config = load_json(hysteria_config_file)
    for item in hysteria_config["auth"]["config"]:
        if item == user_info["password"]:
            hysteria_config["auth"]["config"].remove(item)

    save_json(hysteria_config, hysteria_config_file)


def configure_hysteria_client(user_info: dict, proxy_config: dict, cert_config: dict):
    from base.config import PUBLIC_IP

    client_config = load_json(HYSTERIA_CLIENT_TEMPLATE_CONFIG_FILE)

    client_config["server_name"] = cert_config["FAKE_SNI"]
    client_config["auth_str"] = user_info["password"]

    if proxy_config["OBFS"]:
        client_config["server"] = f"{PUBLIC_IP}:8443"
        client_config["obfs"] = proxy_config["OBFS"]
    else:
        client_config["server"] = f"{PUBLIC_IP}:443"

    if proxy_config["ALPN"]:
        client_config["alpn"] = proxy_config["ALPN"]

    save_json(
        client_config, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria.json"
    )

    if {proxy_config["OBFS"]}:
        share_url = f"hysteria://{PUBLIC_IP}:8443/?insecure=1&peer={cert_config['FAKE_SNI']}&auth={user_info['password']}&alpn={proxy_config['ALPN']}&obfs=xplus&obfsParam={proxy_config['OBFS']}#{user_info['name']}%20Hysteria"
    else:
        share_url = f"hysteria://{PUBLIC_IP}:443/?insecure=1&peer={cert_config['FAKE_SNI']}&auth={user_info['password']}&alpn={proxy_config['ALPN']}#{user_info['name']}%20Hysteria"

    write_txt_file(
        share_url, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/hysteria-url.txt"
    )
