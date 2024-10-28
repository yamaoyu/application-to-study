from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from lib.security import create_access_token

# 以下の変数はconftestで作成していないユーザー用で値を変更しない
another_test_user = "testuser2"
test_password = "password"
test_action = "create test"


def setup_create_todo(client, get_headers):
    data = {"action": test_action, "username": test_username}
    client.post("/todos", json=data, headers=get_headers)


def setup_finish_todo(client, get_headers):
    client.put("/todos/finish/1", headers=get_headers)


def setup_create_another_user(client):
    user_info = {
        "username": another_test_user,
        "password": test_password
    }
    client.post("/users", json=user_info)


def setup_login(client):
    user_info = {
        "username": another_test_user,
        "password": test_password
    }
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    return access_token


def test_create_todo(client, get_headers):
    data = {"action": test_action, "username": test_username}
    response = client.post("/todos", json=data, headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {"message": "以下の内容で作成しました",
                               "action": test_action}


def test_create_todo_without_login(client):
    """ ログインしていない状態で作成した場合 """
    data = {"action": test_action, "username": test_username}
    response = client.post("/todos", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_todo_with_expired_token(client):
    """ 期限の切れたトークンでタスクを作成しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("lib.security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"action": test_action, "username": test_username}
        response = client.post("/todos", json=data, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_create_todo_with_same_content(client, get_headers):
    """ 同じ内容を登録した場合 """
    setup_create_todo(client, get_headers)
    data = {"action": test_action, "username": test_username}
    response = client.post("/todos", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "既に登録されている内容です"}


def test_get_all_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.get("/todos", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == [{"todo_id": 1,
                               "action": test_action,
                                "status": False,
                                "username": test_username}]


def test_get_all_todo_without_login(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.get("/todos")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_todo_with_expired_token(client, get_headers):
    """ 期限の切れたトークンでタスクを取得しようとした場合 """
    def mock_create_access_token(data, minutes):
        expires_delta = timedelta(minutes=minutes)
        return create_access_token(data, expires_delta)

    setup_create_todo(client, get_headers)
    with patch("lib.security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username},
                                                minutes=-30)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/todos", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_all_todo_without_register(client, get_headers):
    """ 作成したタスクが1つもない状態でget """
    response = client.get("/todos", headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "登録された情報はありません"}


def test_get_specific_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.get("/todos/1", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"todo_id": 1,
                               "action": test_action,
                               "status": False,
                               "username": test_username}


def test_get_todo_by_another_user(client, get_headers):
    """ 他のユーザーが作成したタスクの取得はできない """
    setup_create_todo(client, get_headers)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/todos/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "1の情報は未登録です"}


def test_delete_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.delete("/todos/1", headers=get_headers)
    assert response.status_code == 204


def test_delete_todo_by_another_user(client, get_headers):
    """ 他のユーザーが作成したタスクを削除しようとする """
    setup_create_todo(client, get_headers)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/todos/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたタスクは存在しません"}


def test_delete_todo_not_exist(client, get_headers):
    """ 存在しないタスクを削除しようとした場合 """
    response = client.delete("/todos/1", headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたタスクは存在しません"}


def test_edit_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    data = {"action": "new action"}
    response = client.put("/todos/1", json=data, headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"更新後のタスク:{data['action']}"}


def test_edit_todo_by_another_user(client, get_headers):
    """ 他のユーザーが作成したタスクを更新した場合 """
    setup_create_todo(client, get_headers)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"action": "new action"}
    response = client.put("/todos/1", json=data, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "id:1のデータは登録されていません"}


def test_edit_todo_without_login(client, get_headers):
    """ ログインせずに更新しようとした場合 """
    setup_create_todo(client, get_headers)
    data = {"action": "new action"}
    response = client.put("/todos/1", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_finish_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.put("/todos/finish/1", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"message": "以下のタスクのステータスを終了にしました",
                               "action": test_action,
                               "status": True}


def test_finish_todo_before_create_todo(client, get_headers):
    """ 登録されていないタスクを終了しようとした場合 """
    response = client.put("/todos/finish/1", headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "1の内容は登録されていません"}


def test_finish_todo_already_finished(client, get_headers):
    """ 既に終了したタスクを終了しようとした場合 """
    setup_create_todo(client, get_headers)
    setup_finish_todo(client, get_headers)
    response = client.put("/todos/finish/1", headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "既に終了したタスクです"}
