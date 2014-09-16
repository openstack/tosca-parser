#!/bin/bash

cat > /opt/node/config.js<<EOF
{
  "host": "${host}"
  , "port": ${port}
}
EOF