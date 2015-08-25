#!/bin/sh
sed --regexp-extended "s/(port\s*=\s*)[0-9]*/\1$db_port/g" </etc/mysql/my.cnf >/tmp/my.cnf
mv -f /tmp/my.cnf /etc/mysql/my.cnf
/etc/init.d/mysql stop
/etc/init.d/mysql start