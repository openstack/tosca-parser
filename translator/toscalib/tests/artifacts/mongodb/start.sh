#!/bin/sh -x
# This script starts mongodb
/etc/init.d/mongodb stop
rm /var/lib/mongod.lock
mongod --dbpath /var/lib/mongodb &
