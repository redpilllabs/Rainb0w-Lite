#!/bin/bash

function fn_gen_insert_x25519_keys() {
    if [ ! -f "/tmp/Xray/xray" ]; then
        curl -L https://github.com/XTLS/Xray-core/releases/download/v1.8.1/Xray-linux-64.zip -o /tmp/Xray.zip
        unzip -d /tmp/Xray /tmp/Xray.zip
    fi

    echo -e "${B_GREEN}>> Generating a x25519 crypto key pair${RESET}"

    keys=$(/tmp/Xray/xray x25519)

    # Extract each key
    private_key=$(echo $keys | awk '{print $3}')
    public_key=$(echo $keys | awk '{print $6}')

    # Update the .toml file
    sed -i "s/PRIVATE_KEY = \"\"/PRIVATE_KEY = \"$private_key\"/g" $HOME/Rainb0w_Lite_Home/rainb0w_config.toml
    sed -i "s/PUBLIC_KEY = \"\"/PUBLIC_KEY = \"$public_key\"/g" $HOME/Rainb0w_Lite_Home/rainb0w_config.toml

}
