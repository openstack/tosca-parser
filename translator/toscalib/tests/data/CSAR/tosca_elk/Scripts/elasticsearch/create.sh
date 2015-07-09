#!/bin/bash
# This script installs java and elasticsearch

apt-get update
apt-get install -y openjdk-7-jre-headless

wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/elasticsearch/1.5/debian stable main" | tee -a /etc/apt/sources.list

apt-get update
apt-get install -y elasticsearch

# set up to run as service
update-rc.d elasticsearch defaults 95 10
