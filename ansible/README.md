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

## 環境変数について
1. env_vars

   アプリ実行に必要な環境変数

2. group_vars
   
   複数ホストで共通して使用する環境変数

3. host_vars
   
   ホスト固有の環境変数


## 実行準備
### groups_varsの設定
- groups_vars/all.yaml
  
  以下を設定
  1. githubリポジトリの接続先
   
    記載したら以下を実行し、暗号化

    ```
    ansible-vault encrypt groups_vars/all.yaml --vault-password-file ansible_vault_pass.txt
    ```


### host_varsの設定
- hosts_vars/serverX.yaml
  
  Xには既存のサーバーに使われている最大値+1に置き換える(server1.yamlがあるなら追加する場合はserver2.yaml)
  
  以下を設定
  1. ipアドレス
  2. 接続ユーザー名
  3. リポジトリ作成先

    その後、以下を実行し、暗号化

    ```
    ansible-vault encrypt host_vars/server1.yaml --vault-password-file ansible_vault_pass.txt
    ```

### 環境変数の設定
- env_vars/.env.serverX
  
  Xには既存のサーバーに使われている最大値+1に置き換える

  study appで使用する環境変数を設定する

  その後、以下を実行し、暗号化
      ```
    ansible-vault encrypt env_vars/.env.serverX --vault-password-file ansible_vault_pass.txt
    ```

復号時はencrypt→decryptに変更して実行する

## 実行手順
### ディレクトリ移動
playbookのあるディレクトリへ移動する

### playbookの実行
playbook実行時は以下を実行する
```
ansible-playbook -i inventory.yaml playbook.yaml --vault-password-file ansible_vault_pass.txt --ask-become-pass
```
ansible_userのパスワードを聞かれるため、それを入力するとansibleが起動される