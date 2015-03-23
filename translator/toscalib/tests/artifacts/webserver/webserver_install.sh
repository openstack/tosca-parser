#!/bin/sh -x
yum -y install httpd
systemctl enable httpd.service
