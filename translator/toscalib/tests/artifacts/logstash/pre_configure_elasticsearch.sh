#!/usr/bin/python
# This script configures the logstash output to forward to elasticsearch
# The environment variable elasticsearch_ip is expected to be set up
import os
with open("/etc/logstash/elasticsearch.conf", 'w') as fh:
    fh.write("""
      output {
        elasticsearch {
          action => index
          host => "%s"
        }
      }""" % (os.environ['elasticsearch_ip']))
