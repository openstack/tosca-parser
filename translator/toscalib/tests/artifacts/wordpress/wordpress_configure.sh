#!/bin/sh -x
sed -i "/Deny from All/d" /etc/httpd/conf.d/wordpress.conf
sed -i "s/Require local/Require all granted/" /etc/httpd/conf.d/wordpress.conf
sed -i s/database_name_here/db_name/ /etc/wordpress/wp-config.php
sed -i s/username_here/db_user/ /etc/wordpress/wp-config.php
sed -i s/password_here/db_password/ /etc/wordpress/wp-config.php
systemctl restart httpd.service
