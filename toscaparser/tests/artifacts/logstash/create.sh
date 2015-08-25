#!/bin/bash
# This script installs java, logstash and the contrib package for logstash
# install java as prereq

apt-get update
apt-get install -y openjdk-7-jre-headless
mkdir /etc/logstash

# install by apt-get from repo
wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/logstash/1.4/debian stable main" | tee -a /etc/apt/sources.list

apt-get update
apt-get install -y logstash

# install contrib to get the relp plugin
/opt/logstash/bin/plugin install contrib

# set up to run as service
update-rc.d logstash defaults 95 10
