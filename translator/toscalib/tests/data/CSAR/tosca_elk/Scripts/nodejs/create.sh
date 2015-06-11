#!/bin/sh -x
# This script installs nodejs and the prereq
add-apt-repository ppa:chris-lea/node.js

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
apt-get install -y nodejs build-essential
