#!/bin/bash
# This script installs kibana and sets it up to run as a service in init.d
cd /opt
wget https://download.elastic.co/kibana/kibana/kibana-4.1.0-linux-x64.tar.gz
tar xzvf kibana-4.1.0-linux-x64.tar.gz
mv kibana-4.1.0-linux-x64 kibana

# set up to run as service
cd /etc/init.d
wget https://gist.githubusercontent.com/thisismitch/8b15ac909aed214ad04a/raw/bce61d85643c2dcdfbc2728c55a41dab444dca20/kibana4
chmod +x kibana4
update-rc.d kibana4 defaults 96 9
