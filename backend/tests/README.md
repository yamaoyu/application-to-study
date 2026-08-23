# 実行コマンド

- ローカルで実行する場合

``` sh
docker compose exec -e ENV=test backend python -m pytest
```

```sh
# 特定のフォルダにあるテストを実行
docker compose exec -e ENV=test backend python -m pytest tests/routers/inquiry/*.py -vv
```

- 開発コンテナで実行する場合

``` sh
ENV=test LOGFILE_PATH=/tmp/test.log python -m pytest
```

-eオプションを使い、ENVをテストに設定する必要がある  
これはログイン時にリフレッシュトークンとデバイスID発行され、  cookieに保存されるがテスト環境ではHTTPS通信ではなく、HTTPで通信されるためである  
ENVが「test」の場合はsecureがFalseになるようにしているため指定する必要がある

そうでないとtest_regenerate_token()が成功しない
