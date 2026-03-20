### 概要
勉強など努力をすればするほど給料が増えていく
努力した時間を給料に変換して可視化するアプリ

### 起動手順
1. 環境変数の設定  
    .env.templateを.envという名前でコピーして値を設定する  
    コンテナ起動時に.env.templateを見て必要な環境変数を確認し、.envを見て値が設定されているかを確認している
2. コンテナ起動
    ```
    # httpで起動
    bash docker_exec.sh -d
    # httpsで起動
    docker_exec.sh --profile https -d
    ```
    docker_exec.shに引数を渡すことで「docker compose up」にオプションを設定できる