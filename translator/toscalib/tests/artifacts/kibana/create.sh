#!/bin/sh -x
# This script installs kibana and sets it up to run as a service in init.d
mkdir /opt/kibana
cd /opt/kibana
wget https://download.elasticsearch.org/kibana/kibana/kibana-4.0.1-linux-x64.tar.gz
tar xzvf kibana-4.0.1-linux-x64.tar.gz

# set up to run as service
cd /etc/init.d
wget https://gist.githubusercontent.com/thisismitch/8b15ac909aed214ad04a/raw/bce61d85643c2dcdfbc2728c55a41dab444dca20/kibana4
chmod +x kibana4
sed -i 's/KIBANA_BIN=\/opt\/kibana\/bin/KIBANA_BIN=\/opt\/kibana\/kibana-4.0.1-linux-x64\/bin/' kibana4
update-rc.d kibana4 defaults 96 9
