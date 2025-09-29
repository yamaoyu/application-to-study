## 実行内容
- アプリ実行ディレクトリ作成
- gitリポジトリ作成
- 環境変数を規定ファイルに設定していること
- dockerインストール
- docker起動
- フロントエンドで使用する画像が実行マシンにあること

## 実行条件
- sudoができるユーザーであること
- ansibleで使用するユーザーの作成、sshキーの作成、sshキーのgithubへの追加が実施済みであること
- 以下のコレクションがコントロールノードにインストールされていること
  - ansible-galaxy collection install community.general
  - ansible-galaxy collection install community.docker
- ansibleディレクトリにansible_vault_pass.txtを作成し、ansible valutのパスワードを記載する

## 環境変数について
1. env_vars

   アプリ実行に必要な環境変数

2. group_vars
   
   複数ホストで共通して使用する環境変数

3. host_vars
   
   ホスト固有の環境変数


## 実行準備
### env_varsの設定
- env_vars/.env.serverX<br>
  git clone後、env_vars/template-env.serverXを.env.serverXにリネームし、必要箇所を埋める
  
  Xには既存のサーバーに使われている最大値+1に置き換える<br>
  ansibleでは.envと.env.backendの２つのファイルで管理している環境変数全てを.env.serverXで管理する

  study appで使用する環境変数を設定する

  - 暗号時
  ```
  ansible-vault encrypt env_vars/.env.serverX --vault-password-file ansible_vault_pass.txt
  ```
  - 復号時
   ```
  ansible-vault decrypt env_vars/.env.serverX --vault-password-file ansible_vault_pass.txt
  ```

### groups_varsの設定
- group_vars/all.yaml<br>
  git clone後、group_vars/template-all.yamlをall.yamlにリネームし、必要箇所を埋める
  
  以下を設定
  1. githubリポジトリの接続先
   
    記載したら以下を実行し、暗号化

    - 暗号時
    ```
    ansible-vault encrypt group_vars/all.yaml --vault-password-file ansible_vault_pass.txt
    ```
    - 復号時
    ```
    ansible-vault decrypt group_vars/all.yaml --vault-password-file ansible_vault_pass.txt
    ```

### host_varsの設定
- host_vars/serverX.yaml<br>
  git clone後、host_vars/template-serverX.yamlをserverX.yamlにリネームし、必要箇所を埋める
  
  Xには既存のサーバーに使われている最大値+1に置き換える(server1.yamlがあるなら追加する場合はserver2.yaml)
  
  以下を設定
  1. ipアドレス
  2. 接続ユーザー名
  3. リポジトリ作成先

  その後、以下を実行し、暗号化

  - 暗号時
  ```
  ansible-vault encrypt host_vars/serverX.yaml --vault-password-file ansible_vault_pass.txt
  ```

  - 復号時
  ```
  ansible-vault decrypt host_vars/serverX.yaml --vault-password-file ansible_vault_pass.txt
  ```


## 実行手順
### ディレクトリ移動
playbookのあるディレクトリへ移動する

### playbookの実行
playbook実行時は以下を実行する
```
ansible-playbook -i inventory.yaml playbook.yaml --vault-password-file ansible_vault_pass.txt --ask-become-pass　(--limit ホスト名)
```
ansible_userのパスワードを聞かれるため、それを入力するとansibleが起動される
limitオプションは対象となるマネージドノードを制限する時に使用する