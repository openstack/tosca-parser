#!/usr/bin/python
# This script configures the logstash input using the udp protocol on
# port 25826.  This is intended to receive data from collectd from
# any source
import os
with open("/etc/logstash/collectd.conf", "w") as fh:
   fh.write("""
     input {
       udp {
         port => 25826         # 25826 is the default for collectd
         buffer_size => 1452   # 1452 is the default for collectd
         codec => collectd { }
         tags => ["metrics"]
         type => "collectd"
       }
     }""")
