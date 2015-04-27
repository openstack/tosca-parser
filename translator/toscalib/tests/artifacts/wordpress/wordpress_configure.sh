#!/bin/sh
ln -s /usr/share/wordpress /var/www/html/wordpress
gzip -d /usr/share/doc/wordpress/examples/setup-mysql.gz
echo $wp_db_password | bash /usr/share/doc/wordpress/examples/setup-mysql -e $wp_db_name -u $wp_db_user localhost