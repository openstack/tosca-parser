#!/bin/bash
# This script installs nodejs and the prereq

add-apt-repository ppa:chris-lea/node.js

apt-get update
apt-get install -y nodejs build-essential
