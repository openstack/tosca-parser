#!/bin/bash
# This script installs java, logstash and the contrib package for logstash
# install java as prereq

#The while loops in the script, which are added as a workaround to
#make sure multiple apt-get's do not run simultaneously, can be removed
#safely if an orchestrator executing this script is handling the situation.

#Trying to avoid multiple apt-get's running simultaneously (in the
#rare occasion that the apt-get command fails rerun the script).
while [[ "$(ps -A | grep apt-get | awk '{print $1}')" != "" ]]; do
    echo "Waiting for the other apt-get process to complete ..."
    r=$RANDOM && let "sec=$r/10000" && let "mil=($r%10000)/10"
    sleep $sec.$mil
done
apt-get update

#Trying to avoid multiple apt-get's running simultaneously (in the
#rare occasion that the apt-get command fails rerun the script).
while [[ "$(ps -A | grep apt-get | awk '{print $1}')" != "" ]]; do
    echo "Waiting for the other apt-get process to complete ..."
    r=$RANDOM && let "sec=$r/10000" && let "mil=($r%10000)/10"
    sleep $sec.$mil
done
apt-get install -y openjdk-7-jre-headless
mkdir /etc/logstash

# install by apt-get from repo
wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/logstash/1.4/debian stable main" | tee -a /etc/apt/sources.list

#Trying to avoid multiple apt-get's running simultaneously (in the
#rare occasion that the apt-get command fails rerun the script).
while [[ "$(ps -A | grep apt-get | awk '{print $1}')" != "" ]]; do
    echo "Waiting for the other apt-get process to complete ..."
    r=$RANDOM && let "sec=$r/10000" && let "mil=($r%10000)/10"
    sleep $sec.$mil
done
apt-get update

#Trying to avoid multiple apt-get's running simultaneously (in the
#rare occasion that the apt-get command fails rerun the script).
while [[ "$(ps -A | grep apt-get | awk '{print $1}')" != "" ]]; do
    echo "Waiting for the other apt-get process to complete ..."
    r=$RANDOM && let "sec=$r/10000" && let "mil=($r%10000)/10"
    sleep $sec.$mil
done
apt-get install -y logstash

# install contrib to get the relp plugin
/opt/logstash/bin/plugin install contrib

# set up to run as service
update-rc.d logstash defaults 95 10
