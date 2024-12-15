## 実行内容
- アプリ実行ディレクトリ作成
- gitリポジトリ作成
- 環境変数設定
- dockerインストール
- docker起動

## 実行手順
ユーザーの作成、sshキーの作成、sshキーをgithubに追加は手動で行う

groups_vars/all.yamlにgithubのリポジトリとリポジトリを作成するディレクトリ名を記載し、暗号化
'''
ansible-vault encrypt groups_vars/all.yaml  
'''

hosts_vars/server1.yamlにipアドレスと接続ユーザー名を記載し、暗号化
'''
ansible-vault encrypt hosts_vars/server1.yaml  
'''

復号時はencrypt→decryptに変更して実行する

playbook実行時は以下を実行する
'''
ansible-playbook -i inventory.yaml playbook.yaml --vault-password-file ansible_vault_pass.txt --ask-become-pass
'''
ansible_userのパスワードを聞かれるため、それを入力するとansibleが起動される