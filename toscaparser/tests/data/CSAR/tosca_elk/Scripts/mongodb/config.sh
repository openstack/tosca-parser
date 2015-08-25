#!/bin/bash
# Edit the file /etc/mongod.conf, update with real IP of Mongo server
# This script configures the mongodb server to export its service on
# the server IP
# bind_ip = 127.0.0.1     -> bind_ip = <IP for Mongo server>
# The environment variable mongodb_ip is expected to be set up
sed -i "s/= 127.0.0.1/= $mongodb_ip,127.0.0.1/" /etc/mongod.conf
