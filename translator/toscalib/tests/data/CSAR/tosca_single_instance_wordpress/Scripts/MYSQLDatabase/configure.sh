#!/bin/sh
cat << EOF | mysql -u root --password=$db_root_password
CREATE DATABASE $db_name;
GRANT ALL PRIVILEGES ON $db_name.* TO "$db_user"@"localhost"
IDENTIFIED BY "$db_password";
FLUSH PRIVILEGES;
EXIT
EOF