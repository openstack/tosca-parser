#!/bin/bash
#This script installs mysql server

apt-get update

debconf-set-selections <<< "mysql-server mysql-server/root_password password $db_root_password"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $db_root_password"

apt-get -y install --fix-missing mysql-server