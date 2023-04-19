import urllib.parse

from utils.helper import (
    bytes_to_hex,
    bytes_to_url_safe_base64,
    load_toml,
    load_yaml,
    save_toml,
    save_yaml,
)

# MTProtoPy users are loaded directly from 'rainb0w_users.toml'


def configure_mtproto(
    proxy_config: dict,
    cert_config: dict,
    mtproto_config_file: str,
    mtproto_docker_compose_file: str,
):
    print("Configuring MTProto...")
    mtproto_config = load_toml(mtproto_config_file)
    mtproto_docker_compose = load_yaml(mtproto_docker_compose_file)

    mtproto_config["mtproto"]["mask_host"] = cert_config["FAKE_SNI"]
    mtproto_config["mtproto"]["sni"] = cert_config["FAKE_SNI"]
    mtproto_config["server"]["port"] = proxy_config["PORT"]
    mtproto_docker_compose["services"]["mtproto"]["ports"] = [
        f"{proxy_config['PORT']}:{proxy_config['PORT']}"
    ]

    save_toml(mtproto_config, mtproto_config_file)
    save_yaml(mtproto_docker_compose, mtproto_docker_compose_file)


def print_mtproto_share_links(
    user_info: dict,
    proxy_config: dict,
    cert_config: dict,
    base64_encode=False,
):
    from base.config import PUBLIC_IP

    tg_prefix = (
        "tg://"
        + "proxy?server="
        + PUBLIC_IP
        + f"&port={proxy_config['PORT']}"
        + "&secret="
    )
    https_prefix = (
        "https://t.me/"
        + "proxy?server="
        + PUBLIC_IP
        + f"&port={proxy_config['PORT']}"
        + "&secret="
    )
    tls_bytes = (
        bytes.fromhex("ee" + user_info["secret"]) + cert_config["FAKE_SNI"].encode()
    )

    if base64_encode:
        base64_faketls = bytes_to_url_safe_base64(tls_bytes)
        return f"""
*********************** MTPROTO ***********************

Telegram in-app link: {tg_prefix + base64_faketls}
Universal HTTPS link: {https_prefix + base64_faketls}
        """
    else:
        hex_faketls = urllib.parse.quote_plus(bytes_to_hex(tls_bytes))
        return f"""
*********************** MTPROTO ***********************

Telegram in-app link: {tg_prefix + hex_faketls}
Universal HTTPS link: {https_prefix + hex_faketls}
        """
