#!/usr/bin/python
# This script configures the logstash input using the RELP protocol on
# port 2514  This is intended to receive logs from rsyslog from
# any source
import os
with open("/etc/logstash/rsyslog.conf", "w") as fh:
   fh.write("""
   input {
     relp {
       port => 2514
       tags => ["logs"]
     }
   }""")

