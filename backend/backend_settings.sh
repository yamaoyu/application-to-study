#!/bin/bash

if [ ! -d "alembic" ]; then
    alembic init alembic
    echo "alembic initialized"
else
    echo "alembic already initialized"

fi


# バックエンドで使用する環境変数一覧
env_vars=(
    "TEST_MYSQL_DATABASE" "TEST_DATABASE_URL" "APP_ADMIN_USER" "APP_ADMIN_PASSWORD" 
    "FRONTEND_URL" "ENV" "SECRET_KEY" "ALGORITHM" "PEPPER" "BACKEND_PORT" 
    "ACCESS_TOKEN_EXPIRE_MINUTES" "REFRESH_TOKEN_EXPIRE_WEEKS"
    )

for VAR in "${env_vars[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "環境変数未設定---------------"
        echo $VAR
        echo "---------------------------"
        exit 1  # 環境変数が設定されていない→終了
    fi
done

# ログファイル確認
if [ $ENV = "DEV" ]; then
    if [ -z $DEV_LOGFILE_PATH ]; then
        echo "DEV_LOGFILE_PATHが未設定"
        exit 1
    fi
else
    if [ -z $LOGFILE_PATH ]; then
        echo "LOGFILE_PATHが未設定"
        exit 1
    fi
fi

python settings.py

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload