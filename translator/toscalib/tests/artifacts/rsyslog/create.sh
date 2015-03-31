#!/bin/sh -x
# This script installs rsyslog and the library for RELP
apt-get update
apt-get install -y rsyslog
apt-get update
apt-get install -y rsyslog-relp
