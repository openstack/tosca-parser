#!/bin/bash
# This script starts mongodb
service mongod stop
rm /var/lib/mongodb/mongod.lock
service mongod start
