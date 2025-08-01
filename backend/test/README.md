# 実行コマンド
```
# 全てのテストを実行
docker compose exec -e ENV=test backend python -m pytest
```
-eオプションを使い、ENVをテストに設定する必要がある<br>
これはログイン時にリフレッシュトークンとデバイスID発行され、cookieに保存されるがテスト環境ではHTTPS通信ではなく、<br>
HTTPで通信されるためである<br>
ENVが「test」の場合はsecureがFalseになるようにしているため指定する必要がある<br>
そうでないとtest_regenerate_token()が成功しない