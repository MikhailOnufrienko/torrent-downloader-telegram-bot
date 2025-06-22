#!/bin/sh
# Extract password of the qbittorrent client and write it down to the .env file.

CONTAINER_NAME=qbittorrent-cont
ENV_FILE_PATH=.env

export UID=$(id -u)
export GID=$(id -g)

docker compose up --build -d qbittorrent

sleep 3

PASSWORD=$(
    docker logs $CONTAINER_NAME 2>&1 | \
    grep "A temporary password" | \
    tail -n 1| \
    awk -F'session: ' '{print $2}' | \
    tr -d ' ' | \
    cut -c1-9
)

sed -i '/^QBITTORRENT_AUTH_PASS=/d' $ENV_FILE_PATH
echo "QBITTORRENT_AUTH_PASS=$PASSWORD" >> $ENV_FILE_PATH

docker compose up --build -d db
