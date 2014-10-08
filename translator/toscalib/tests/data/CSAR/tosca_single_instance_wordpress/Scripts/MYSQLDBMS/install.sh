#!/bin/sh -x
yum -y install mysql mysql-server
# Use systemd to start MySQL server at system boot time
#systemctl enable mysqld.service
