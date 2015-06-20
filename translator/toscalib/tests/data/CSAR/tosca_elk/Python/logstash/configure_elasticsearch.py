#!/usr/bin/python

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This script configures the logstash output to forward to elasticsearch
# The environment variable elasticsearch_ip is expected to be set up
import os
with open("/etc/logstash/conf.d/elasticsearch.conf", 'w') as fh:
    fh.write("""
      output {
        elasticsearch {
          action => index
          host => "%s"
          protocol => "http"
        }
      }""" % (os.environ['elasticsearch_ip']))
