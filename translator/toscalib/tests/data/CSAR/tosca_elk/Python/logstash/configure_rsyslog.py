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

# This script configures the logstash input using the RELP protocol on
# port 2514  This is intended to receive logs from rsyslog from
# any source
with open("/etc/logstash/conf.d/rsyslog.conf", "w") as fh:
    fh.write("""
    input {
      relp {
        port => 2514
        tags => ["logs"]
      }
    }""")
