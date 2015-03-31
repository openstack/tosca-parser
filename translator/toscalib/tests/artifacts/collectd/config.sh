#!/usr/bin/python
# This script configures collectd to send metric data to the
# logstash server port 25826
# The environment variable logstash_ip is expected to be set up
import os
with open("/etc/collectd/collectd.conf.d/tosca_elk.conf", "w") as fh:
   fh.write("""
LoadPlugin network

<Plugin network>
        Server "%s" "25826"
</Plugin>

""" % (os.environ['logstash_ip']))
