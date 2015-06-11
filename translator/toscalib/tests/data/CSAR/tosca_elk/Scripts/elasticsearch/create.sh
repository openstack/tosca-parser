#!/bin/sh -x
# This script installs java and elasticsearch

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

wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/elasticsearch/1.5/debian stable main" | tee -a /etc/apt/sources.list

#Trying to avoid multiple apt-get's running simultaneously (in the
#rare occasion that the apt-get command fails rerun the script).
while [[ "$(ps -A | grep apt-get | awk '{print $1}')" != "" ]]; do
    echo "Waiting for the other apt-get process to complete ..."
    r=$RANDOM && let "sec=$r/10000" && let "mil=($r%10000)/10"
    sleep $sec.$mil
done
apt-get install -y elasticsearch

# set up to run as service
update-rc.d elasticsearch defaults 95 10
