#!/bin/bash

# This script configures the output for rsyslogd to send logs to the
# logstash server port 2514 using the RELP protocol
# The environment variable logstash_ip is expected to be set up
echo "module(load=\"omrelp\")
action(type=\"omrelp\" target=\"$logstash_ip\" port=\"2514\")" > /etc/rsyslog.d/tosca_elk.conf

# Remove the /dev/xconsole configuration as xconsole
# is not available by default
l=`awk '/=warn.*\|.*\/dev\/xconsole/{print NR - 1}' /etc/rsyslog.d/50-default.conf`
if [ ! -z $l ]; then
    l=`expr $l + 1`
    line=`cat /etc/rsyslog.d/50-default.conf | head -n $l | tail -1`
    if [[ ! $line == \#* ]]; then
       l0=`expr $l - 3`
       sed -i -r -e "${l0},${l}s/^.{0}/&#/" /etc/rsyslog.d/50-default.conf
    fi
fi

# Enable nodejs logs for rsyslog
if ! grep -q nodeapp "/etc/rsyslog.conf"; then
    sed -i 's/\$PrivDropToGroup\ syslog/\$PrivDropToGroup adm/' /etc/rsyslog.conf
    echo "\$ModLoad imfile.so
\$InputFileName /var/log/nodeapp.log
\$InputFileTag paypal_pizza:
\$InputFileStateFile stat-nodeapp
\$InputRunFileMonitor
\$InputFilePollInterval 1" >> /etc/rsyslog.conf
fi
