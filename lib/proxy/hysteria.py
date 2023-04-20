import base64

from base.config import CLIENT_CONFIG_FILES_DIR, HYSTERIA_CLIENT_TEMPLATE_CONFIG_FILE
from utils.helper import bytes_to_raw_str, load_json, load_yaml, save_json, save_yaml


def prompt_hysteria_alpn():
    print(
        """
[Optional | Recommended] Enter an ALPN value for Hysteria packets.
If you're using a common port for Hysteria, it's recommended to match
it with the actual ALPN value of legitimate traffic on that port!
If you're using an uncommon port, you can leave this blank or set a random ALPN.

You can see a brief list of common ports and their corresponding ALPNs:
    - 443/udp:  h3
    - 554/udp:  rtsp
    - 8443/udp: h3  OR  webrtc
        """
    )
    alpn = input("\nEnter your desired ALPN: ")
    if alpn:
        return alpn
    else:
        return None


def prompt_hysteria_obfs():
    print(
        """
[Optional | Recommended] Enter a random and strong password to obfuscate the Hysteria traffic.
Leaving this blank, will DISABLE the obfuscation and your traffic will be known as normal QUIC traffic.
Usually you need to fill this, since QUIC is mostly blocked in Iran.

NOTE: If you're trying to closely match the QUIC traffic characteristics
you need to leave this blank and use the port 443/udp and the 'h3' ALPN as they
are the official specs for QUIC traffic.
        """
    )
    obfs = input("\nEnter a random obfuscation password: ")
    if obfs:
        return obfs
    else:
        return None


def configure_hysteria(
    proxy_config: dict, hysteria_config_file: str, hysteria_docker_compose_file: str
):
    print("Configuring Hysteria...")
    hysteria_config = load_json(hysteria_config_file)
    hysteria_docker_compose = load_yaml(hysteria_docker_compose_file)

    hysteria_config["listen"] = f":{proxy_config['PORT']}"
    hysteria_docker_compose["services"]["hysteria"]["ports"] = [
        f"{proxy_config['PORT']}:{proxy_config['PORT']}/udp"
    ]
    if proxy_config["OBFS"]:
        hysteria_config["obfs"] = proxy_config["OBFS"]
    if proxy_config["ALPN"]:
        hysteria_config["alpn"] = proxy_config["ALPN"]

    save_json(hysteria_config, hysteria_config_file)
    save_yaml(hysteria_docker_compose, hysteria_docker_compose_file)


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

    client_config["server"] = f"{PUBLIC_IP}:{proxy_config['PORT']}"
    client_config["server_name"] = cert_config["FAKE_SNI"]
    client_config["auth"] = bytes_to_raw_str(
        base64.b64encode(user_info["password"].encode())
    )
    if proxy_config["OBFS"]:
        client_config["obfs"] = proxy_config["OBFS"]
    if proxy_config["ALPN"]:
        client_config["alpn"] = proxy_config["ALPN"]

    save_json(
        client_config, f"{CLIENT_CONFIG_FILES_DIR}/{user_info['name']}-hysteria.json"
    )


def print_hysteria_client_info(user_info: dict, proxy_config: dict, cert_config: dict):
    from base.config import PUBLIC_IP

    return f"""
*********************** HYSTERIA ***********************

Server:             {PUBLIC_IP}
Port:               {proxy_config['PORT']}
Protocol:           UDP
SNI:                {cert_config['FAKE_SNI']}
ALPN:               {proxy_config['ALPN']}
Obfuscation:        {proxy_config['OBFS']}
Auth. Type:         BASE64
Payload:            {bytes_to_raw_str(base64.b64encode(user_info["password"].encode()))}
Allow Insecure:     Enabled
Max Upload:         YOUR REAL UPLOAD SPEED
Max Download:       YOUR REAL DOWNLOAD SPEED
QUIC Stream:        1677768
QUIC Conn.:         4194304
Disable Path MTU Discovery: Enabled
    """
