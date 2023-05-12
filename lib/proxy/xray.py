from base.config import (
    CLIENT_CONFIG_FILES_DIR,
    PUBLIC_IP,
    XRAY_CLIENT_TEMPLATE_CONFIG_FILE,
)
from utils.cert_utils import is_subdomain
from utils.helper import load_json, save_json, write_txt_file


def xray_add_user(user_info: dict, xray_config_file: str):
    config = load_json(xray_config_file)
    new_client = {
        "email": user_info["name"],
        "id": user_info["uuid"],
        "flow": "xtls-rprx-vision",
        "level": 0,
    }
    config["inbounds"][0]["settings"]["clients"].append(new_client)
    config["inbounds"][0]["streamSettings"]["realitySettings"]["shortIds"].append(
        user_info["short_id"]
    )

    save_json(config, xray_config_file)


def xray_remove_user(user_info: dict, xray_config_file: str):
    config = load_json(xray_config_file)
    if "clients" in config["inbounds"][0]["settings"]:
        for client in config["inbounds"][0]["settings"]["clients"]:
            if client["email"] == user_info["name"]:
                config["inbounds"][0]["settings"]["clients"].remove(client)
                config["inbounds"][0]["streamSettings"]["realitySettings"][
                    "shortIds"
                ].remove(user_info["short_id"])

    save_json(config, xray_config_file)


def configure_xray_reality(
    proxy_config: dict,
    cert_config: dict,
    xray_config_file: str,
):
    print("Configuring Xray...")
    xray_config = load_json(xray_config_file)

    xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
        "privateKey"
    ] = proxy_config["PRIVATE_KEY"]

    xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
        "dest"
    ] = f"{cert_config['FAKE_SNI']}:443"

    xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
        "serverNames"
    ].append(cert_config["FAKE_SNI"])

    if not is_subdomain(cert_config["FAKE_SNI"]):
        xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
            "serverNames"
        ].append(f"www.{cert_config['FAKE_SNI']}")

    save_json(xray_config, xray_config_file)


def configure_xray_reality_client(
    user_info: dict, proxy_config: dict, cert_config: dict
):
    client_config = load_json(XRAY_CLIENT_TEMPLATE_CONFIG_FILE)

    client_config["outbounds"][0]["settings"]["vnext"][0]["address"] = PUBLIC_IP
    client_config["outbounds"][0]["settings"]["vnext"][0]["port"] = int(
        proxy_config["PORT"]
    )
    client_config["outbounds"][0]["settings"]["vnext"][0]["users"] = [
        {
            "id": user_info["uuid"],
            "encryption": "none",
            "flow": "xtls-rprx-vision-udp443",
        }
    ]
    client_config["outbounds"][0]["streamSettings"]["realitySettings"][
        "serverName"
    ] = cert_config["FAKE_SNI"]
    client_config["outbounds"][0]["streamSettings"]["realitySettings"][
        "publicKey"
    ] = proxy_config["PUBLIC_KEY"]
    client_config["outbounds"][0]["streamSettings"]["realitySettings"][
        "shortId"
    ] = user_info["short_id"]

    share_url = f"vless://{user_info['uuid']}@{PUBLIC_IP}:{proxy_config['PORT']}?security=reality&encryption=none&pbk={proxy_config['PUBLIC_KEY']}&headerType=none&fp=chrome&spx=%2F&type=tcp&flow=xtls-rprx-vision-udp443&sni={cert_config['FAKE_SNI']}&sid={user_info['short_id']}#{user_info['name']}+REALITY"
    write_txt_file(
        share_url, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/reality-url.txt"
    )
    save_json(
        client_config, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/reality.json"
    )


def reset_xray_sni(
    sni: str,
    xray_config_file: str,
):
    xray_config = load_json(xray_config_file)

    xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
        "dest"
    ] = f"{sni}:443"

    xray_config["inbounds"][0]["streamSettings"]["realitySettings"]["serverNames"] = [
        sni
    ]

    if not is_subdomain(sni):
        xray_config["inbounds"][0]["streamSettings"]["realitySettings"][
            "serverNames"
        ].append(f"www.{sni}")

    save_json(xray_config, xray_config_file)
