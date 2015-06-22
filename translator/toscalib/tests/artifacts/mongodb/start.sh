#!/bin/sh -x
# This script starts mongodb
sleep 30
/etc/init.d/mongodb stop
rm /var/lib/mongodb/mongod.lock
mongod --dbpath /var/lib/mongodb --repair
mongod --dbpath /var/lib/mongodb --fork --logpath /var/log/mongod.log --config=/etc/mongodb.conf

