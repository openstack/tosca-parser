#!/bin/bash
echo "conn = new Mongo();"                               > setup.js
echo "db = conn.getDB('paypal_pizza');"                 >> setup.js
echo "db.about.insert({'name': 'PayPal Pizza Store'});" >> setup.js
mongo setup.js
