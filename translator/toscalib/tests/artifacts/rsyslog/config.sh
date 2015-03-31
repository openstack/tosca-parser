#!/usr/bin/python
# This script configures the output for rsyslogd to send logs to the
# logstash server port 2514 using the RELP protocol
# The environment variable logstash_ip is expected to be set up
import os
with open("/etc/rsyslog.d/tosca_elk.conf", "w") as fh:
   fh.write("""
       module(load="omrelp")
       action(type="omrelp" target="%s" port="2514")
       """ % (os.environ['logstash_ip']))
