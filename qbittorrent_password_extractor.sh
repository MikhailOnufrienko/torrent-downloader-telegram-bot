#!/bin/sh
# Extract password of the qbittorrent client and write it down to the .env file.

CONTAINER_NAME=qbittorrent
ENV_FILE_PATH=.env

PASSWORD=$(
    docker logs $CONTAINER_NAME 2>&1 | \
    grep "A temporary password" | \
    tail -n 1| \
    awk -F'session: ' '{print $2}' | \
    tr -d ' ' | \
    cut -c1-9
)

echo "QBITTORRENT_AUTH_PASS=$PASSWORD" >> $ENV_FILE_PATH