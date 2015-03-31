#!/bin/sh -x
# This script configures kibana to connect to the elasticsearch server
# to access data and to export the app url on port 5601:
# The environment variable elasticsearch_ip and kibana_ip are expected
# to be set up.
sed -i 's/localhost/'$elasticsearch_ip'/' /opt/kibana/kibana-4.0.1-linux-x64/config/kibana.yml
sed -i 's/0.0.0.0/'$kibana_ip'/' /opt/kibana/kibana-4.0.1-linux-x64/config/kibana.yml
