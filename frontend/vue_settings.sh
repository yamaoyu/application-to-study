#!/bin/bash
env_vars=("VITE_BACKEND_URL" "VITE_FRONTEND_PORT")

for VAR in "${env_vars[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "環境変数未設定---------------"
        echo $VAR
        echo "---------------------------"
        exit 1  # 環境変数が設定されていない→終了
    fi
done

npm run dev