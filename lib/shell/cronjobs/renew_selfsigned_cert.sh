#!/bin/bash

COMMON_NAME=''

echo -e "${B_GREEN}>> Generating a self-signed certificate${RESET}"
openssl req -newkey rsa:2048 \
    -x509 \
    -nodes \
    -days 365 \
    -out /etc/ssl/certs/selfsigned.crt \
    -keyout /etc/ssl/private/selfsigned.key \
    -subj "/C=US/CN=$COMMON_NAME"
