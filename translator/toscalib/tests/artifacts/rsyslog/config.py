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

# This script configures the output for rsyslogd to send logs to the
# logstash server port 2514 using the RELP protocol
# The environment variable logstash_ip is expected to be set up
import os
with open("/etc/rsyslog.d/tosca_elk.conf", "w") as fh:
    fh.write("""
        module(load="omrelp")
        action(type="omrelp" target="%s" port="2514")
        """ % (os.environ['logstash_ip']))
