#!/bin/bash
env_vars=(
    "MYSQL_ROOT_PASSWORD" "MYSQL_USER" "MYSQL_PASSWORD" 
    "MYSQL_DATABASE" "MYSQL_HOST" "DB_PORT"
    )

for VAR in "${env_vars[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "環境変数未設定---------------"
        echo $VAR
        echo "---------------------------"
        exit 1  # 環境変数が設定されていない→終了
    fi
done

exec docker-entrypoint.sh mysqld