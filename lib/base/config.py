import os

from utils.helper import get_public_ip

# Server info
PUBLIC_IP = get_public_ip()

# Path
RAINB0W_BACKUP_DIR = f"{os.path.expanduser('~')}/Rainb0w_Backup"
RAINB0W_HOME_DIR = f"{os.path.expanduser('~')}/Rainb0w_Lite_Home"
RAINB0W_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/rainb0w_config.toml"
RAINB0W_USERS_FILE = f"{RAINB0W_HOME_DIR}/rainb0w_users.toml"
CLIENT_CONFIG_FILES_DIR = f"{RAINB0W_HOME_DIR}/clients"
XRAY_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/xray/etc/xray.json"
XRAY_CLIENT_TEMPLATE_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/xray/etc/client.json"
XRAY_DOCKER_COMPOSE_FILE = f"{RAINB0W_HOME_DIR}/xray/docker-compose.yml"
HYSTERIA_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/hysteria/etc/hysteria.yml"
HYSTERIA_CLIENT_TEMPLATE_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/hysteria/etc/client.yml"
HYSTERIA_DOCKER_COMPOSE_FILE = f"{RAINB0W_HOME_DIR}/hysteria/docker-compose.yml"
MTPROTOPY_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/mtproto/etc/config.toml"
MTPROTOPY_DOCKER_COMPOSE_FILE = f"{RAINB0W_HOME_DIR}/mtproto/docker-compose.yml"
BLOCKY_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/blocky/etc/config.yml"
