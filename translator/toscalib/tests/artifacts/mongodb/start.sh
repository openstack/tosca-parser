#!/bin/sh -x
# This script starts mongodb
/etc/init.d/mongodb stop
rm /var/lib/mongodb/mongod.lock
mongod --repair
mongod --dbpath /var/lib/mongodb --fork --logpath /var/log/mongod.log
