#!/bin/bash
# This script installs an app for nodejs: the app intended is the paypal app
# and it is configured to connect to the mongodb server
# The environment variables github_url and mongodb_ip are expected to be set up
export app_dir=/opt/app
git clone $github_url /opt/app
if [ -f /opt/app/package.json ]; then
   cd  /opt/app/ && npm install
   sed -i "s/localhost/$mongodb_ip/" config.json
fi

cat > /etc/init/nodeapp.conf <<EOS
description "node.js app"
 
start on (net-device-up
          and local-filesystems
          and runlevel [2345])
stop on runlevel [!2345]
 
expect fork
respawn
 
script
  export HOME=/
  export NODE_PATH=/usr/lib/node
  exec /usr/bin/node ${app_dir}/app.js >> /var/log/nodeapp.log 2>&1 &
end script
EOS
