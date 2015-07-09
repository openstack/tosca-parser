#!/bin/bash
# This script installs mongodb

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list

apt-get update
apt-get install -y mongodb-org

#Wait for mongodb initialization
while [[ ! -d "/var/lib/mongodb/_tmp" ]]; do
    echo "Waiting for mongodb initialization ..."
    sleep 5
done
