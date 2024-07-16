from conftest import test_username

another_user = "another testuser"
password = "password"
action = "create test"


def setup_create_todo(client, login_and_get_token):
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"action": action, "username": test_username}
    client.post("/todo", json=data, headers=headers)


def setup_finish_todo(client, login_and_get_token):
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    client.put("/todo/finish/1", headers=headers)


def setup_create_another_user(client):
    user_info = {"username": another_user,
                 "password": password}
    client.post("/register", json=user_info)


def setup_login(client):
    user_info = {"username": another_user,
                 "password": password}
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    return access_token


def test_create_todo(client, login_and_get_token):
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"action": action, "username": test_username}
    response = client.post("/todo", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"action": action}


def test_create_todo_without_login(client):
    """ ログインしていない状態で作成した場合 """
    data = {"action": action, "username": test_username}
    response = client.post("/todo", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_todo_with_same_content(client, login_and_get_token):
    """ 同じ内容を登録した場合 """
    setup_create_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"action": action, "username": test_username}
    response = client.post("/todo", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "既に登録されている内容です"}


def test_get_all_todo(client, login_and_get_token):
    setup_create_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/todo", headers=headers)
    assert response.status_code == 200
    assert response.json() == [{"todo_id": 1,
                               "action": action,
                                "status": False,
                                "username": test_username}]


def test_get_all_todo_without_login(client, login_and_get_token):
    setup_create_todo(client, login_and_get_token)
    response = client.get("/todo")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_all_todo_without_register(client, login_and_get_token):
    """ 作成したタスクが1つもない状態でget """
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/todo", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "登録された情報はありません。"}


def test_get_specific_todo(client, login_and_get_token):
    setup_create_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/todo/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"todo_id": 1,
                               "action": action,
                               "status": False,
                               "username": test_username}


def test_get_todo_which_another_user_create(client,
                                            login_and_get_token):
    """ 他のユーザーが作成したタスクの取得はできない """
    setup_create_todo(client, login_and_get_token)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/todo/1", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "1の情報は未登録です。"}


def test_delete_todo(client, login_and_get_token):
    setup_create_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/todo/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "選択したタスクを削除しました。"}


def test_delete_todo_which_another_user_create(client, login_and_get_token):
    """ 他のユーザーが作成したタスクを削除しようとする """
    setup_create_todo(client, login_and_get_token)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/todo/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたタスクは存在しません。"}


def test_delete_todo_not_exist(client, login_and_get_token):
    """ 存在しないタスクを削除しようとした場合 """
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/todo/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたタスクは存在しません。"}


def test_edit_todo(client, login_and_get_token):
    setup_create_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"action": "new action"}
    response = client.put("/todo/1", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"更新後のタスク:{data['action']}"}


def test_edit_todo_which_another_user_create(client, login_and_get_token):
    """ 他のユーザーが作成したタスクを更新した場合 """
    setup_create_todo(client, login_and_get_token)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"action": "new action"}
    response = client.put("/todo/1", json=data, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "id:1のデータは登録されていません"}


def test_edit_todo_without_login(client, login_and_get_token):
    """ ログインせずに更新しようとした場合 """
    setup_create_todo(client, login_and_get_token)
    data = {"action": "new action"}
    response = client.put("/todo/1", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_finish_todo(client, login_and_get_token):
    setup_create_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/todo/finish/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"action": action, "status": True}


def test_finish_todo_before_create_todo(client, login_and_get_token):
    """ 登録されていないタスクを終了しようとした場合 """
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/todo/finish/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "1の内容は登録されていません"}


def test_finish_todo_already_finished(client, login_and_get_token):
    """ 既に終了したタスクを終了しようとした場合 """
    setup_create_todo(client, login_and_get_token)
    setup_finish_todo(client, login_and_get_token)
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/todo/finish/1", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "既に終了したタスクです"}
