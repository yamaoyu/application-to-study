#!/bin/bash
set -eu

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -f ".env" ]; then
    echo ".env がありません。.env.template を元に作成してください。"
    exit 1
fi

if [ ! -f ".env.template" ]; then
    echo ".env.template がありません。"
    exit 1
fi

set -a
. ./.env
set +a

required_vars=()
while IFS= read -r line; do
    [ -z "$line" ] && continue
    case "$line" in
        \#*) continue ;;
    esac

    var_name="${line%%=*}"
    required_vars+=("$var_name")
done < .env.template

missing_vars=()
for var_name in "${required_vars[@]}"; do
    if [ -z "${!var_name:-}" ]; then
        missing_vars+=("$var_name")
    fi
done

if [ "${#missing_vars[@]}" -gt 0 ]; then
    echo "環境変数未設定---------------"
    printf '%s\n' "${missing_vars[@]}"
    echo "---------------------------"
    exit 1
fi

docker compose down
docker compose up --build "$@"
