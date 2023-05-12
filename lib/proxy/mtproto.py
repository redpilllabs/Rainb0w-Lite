import urllib.parse

from base.config import CLIENT_CONFIG_FILES_DIR
from utils.helper import (
    bytes_to_hex,
    bytes_to_url_safe_base64,
    load_toml,
    save_toml,
    write_txt_file,
)

# MTProtoPy users are loaded directly from 'rainb0w_users.toml'


def configure_mtproto(
    proxy_config: dict,
    cert_config: dict,
    mtproto_config_file: str,
):
    print("Configuring MTProto...")
    mtproto_config = load_toml(mtproto_config_file)

    mtproto_config["mtproto"]["mask_host"] = cert_config["FAKE_SNI"]
    mtproto_config["mtproto"]["sni"] = cert_config["FAKE_SNI"]
    mtproto_config["server"]["port"] = proxy_config["PORT"]

    save_toml(mtproto_config, mtproto_config_file)


def configure_mtproto_client(
    user_info: dict,
    proxy_config: dict,
    cert_config: dict,
    base64_encode=False,
):
    from base.config import PUBLIC_IP

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
        write_txt_file(
            https_prefix + base64_faketls,
            f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/mtproto-url.txt",
        )
    else:
        hex_faketls = urllib.parse.quote_plus(bytes_to_hex(tls_bytes))
        write_txt_file(
            https_prefix + hex_faketls,
            f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}/mtproto-url.txt",
        )


def reset_mtproto_sni(
    sni: str,
    mtproto_config_file: str,
):
    mtproto_config = load_toml(mtproto_config_file)

    mtproto_config["mtproto"]["mask_host"] = sni
    mtproto_config["mtproto"]["sni"] = sni

    save_toml(mtproto_config, mtproto_config_file)
