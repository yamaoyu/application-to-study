envsubst < /backend/db/init.template.sql > /docker-entrypoint-initdb.d/init.sql
exec /usr/local/bin/docker-entrypoint.sh "$@"