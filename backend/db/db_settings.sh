#!/bin/sh
set -eu

sed \
  -e "s/__MYSQL_DATABASE__/${MYSQL_DATABASE}/g" \
  -e "s/__TEST_MYSQL_DATABASE__/${TEST_MYSQL_DATABASE}/g" \
  -e "s/__MYSQL_USER__/${MYSQL_USER}/g" \
  /init.sql.template > /docker-entrypoint-initdb.d/init.sql

exec docker-entrypoint.sh mysqld
