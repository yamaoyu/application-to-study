from unittest.mock import patch
from datetime import timedelta
from conftest import test_username, another_test_user, password_for_another_user
from lib.security import create_access_token

# 以下の変数はconftestで作成していないユーザー用で値を変更しない
test_title = "create test"
test_due = "2024-11-10"
test_detail = "detail"


def setup_create_todo(client, get_headers):
    data = {"title": test_title, "due": test_due, "detail": test_detail}
    client.post("/todos", json=data, headers=get_headers)


def setup_finish_todo(client, get_headers):
    response = client.put("/todos/finish/1", headers=get_headers)
    print(response.json())


def setup_create_another_user(client):
    user_info = {
        "username": another_test_user,
        "password": password_for_another_user,
    }
    client.post("/users", json=user_info)


def setup_login(client):
    user_info = {
        "username": another_test_user,
        "password": password_for_another_user
    }
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    return access_token


def test_create_todo(client, get_headers):
    data = {"title": test_title, "due": test_due, "detail": test_detail}
    response = client.post("/todos", json=data, headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {"message": "以下の内容で作成しました",
                               "title": test_title,
                               "due": "2024-11-10",
                               "detail": test_detail}


def test_create_todo_without_login(client):
    """ ログインしていない状態で作成した場合 """
    data = {"title": test_title, "username": test_username}
    response = client.post("/todos", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_todo_with_expired_token(client):
    """ 期限の切れたトークンでTodoを作成しようとした場合 """
    def mock_create_expired_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"title": test_title, "username": test_username}
        response = client.post("/todos", json=data, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_create_todos(client, get_headers):
    data = {"todos":
            [
                {"title": test_title, "due": test_due, "detail": test_detail},
                {"title": test_title + "2", "due": test_due, "detail": test_detail + "2"}
            ]
            }
    response = client.post("/todos/multi", json=data, headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {
        "message": f"【Todo作成成功】{test_title}\n【Todo作成成功】{test_title}2"
    }


def test_get_all_todos(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.get("/todos", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == [{"todo_id": 1,
                                "title": test_title,
                                "status": False,
                                "username": test_username,
                                "due": test_due,
                                "detail": test_detail}]


def test_get_todos_with_query_parameters(client, get_headers):
    """ クエリパラメータで活動を絞って取得 """
    setup_create_todo(client, get_headers)
    # ステータスで絞る
    response = client.get("/todos?status=false", headers=get_headers)
    assert response.status_code == 200
    # 期限で絞る(期限外は表示されない)
    response = client.get("/todos?status=false&start_due=2024/11/11", headers=get_headers)
    assert response.status_code == 404


def test_get_all_incomplete_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    setup_finish_todo(client, get_headers)
    data = {"title": "test_2", "due": test_due, "detail": test_detail}
    client.post("/todos", json=data, headers=get_headers)
    response = client.get("/todos?status=False", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == [{"todo_id": 2,
                                "title": "test_2",
                                "status": False,
                                "username": test_username,
                                "due": test_due,
                                "detail": test_detail}]


def test_get_all_todo_without_login(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.get("/todos")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_todo_with_invalid_date(client, get_headers):
    """ 存在しない日付の場合 """
    data = {"title": test_title, "due": "2024-6-31"}
    response = client.post("/todos",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "不正な日付です"}


def test_get_todo_with_expired_token(client, get_headers):
    """ 期限の切れたトークンでTodoを取得しようとした場合 """
    def mock_create_expired_access_token(data, minutes):
        expires_delta = timedelta(minutes=minutes)
        return create_access_token(data, expires_delta)

    setup_create_todo(client, get_headers)
    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": test_username},
                                                        minutes=-30)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/todos", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_all_todo_without_register(client, get_headers):
    """ 作成したTodoが1つもない状態でget """
    response = client.get("/todos", headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "登録された情報はありません"}


def test_get_specific_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.get("/todos/1", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"todo_id": 1,
                               "title": test_title,
                               "status": False,
                               "username": test_username,
                               "due": test_due,
                               "detail": test_detail}


def test_get_todo_by_another_user(client, get_headers):
    """ 他のユーザーが作成したTodoの取得はできない """
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
    """ 他のユーザーが作成したTodoを削除しようとする """
    setup_create_todo(client, get_headers)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/todos/1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたTodoは存在しません"}


def test_delete_todo_not_exist(client, get_headers):
    """ 存在しないTodoを削除しようとした場合 """
    response = client.delete("/todos/1", headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたTodoは存在しません"}


def test_delete_todos(client, get_headers):
    """ 複数Todoの一括削除"""
    for _ in range(2):
        setup_create_todo(client, get_headers)
    data = {"ids": [1, 2]}
    response = client.put("/todos/multi/delete", json=data, headers=get_headers)
    assert response.status_code == 204


def test_delete_todos_not_exist(client, get_headers):
    """ 存在しないTodoを複数削除しようとした場合 """
    data = {"ids": [1, 2]}
    response = client.put("/todos/multi/delete", json=data, headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "削除リクエストされたTodoは全て存在しません"
    }


def test_edit_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    data = {"title": "new title", "due": "2024-11-11", "detail": "new detail"}
    response = client.put("/todos/1", json=data, headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Todoを更新しました",
                               "title": "new title", "due": "2024-11-11", "detail": "new detail"}


def test_edit_todo_by_another_user(client, get_headers):
    """ 他のユーザーが作成したTodoを更新した場合 """
    setup_create_todo(client, get_headers)
    setup_create_another_user(client)
    access_token = setup_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"title": "new title", "due": test_due, "detail": test_detail}
    response = client.put("/todos/1", json=data, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "id:1のデータは登録されていません"}


def test_edit_todo_without_login(client, get_headers):
    """ ログインせずに更新しようとした場合 """
    setup_create_todo(client, get_headers)
    data = {"title": "new title"}
    response = client.put("/todos/1", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_finish_todo(client, get_headers):
    setup_create_todo(client, get_headers)
    response = client.put("/todos/finish/1", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"message": "選択したTodoを終了しました",
                               "title": test_title,
                               "status": True}


def test_finish_todo_before_create_todo(client, get_headers):
    """ 登録されていないTodoを終了しようとした場合 """
    response = client.put("/todos/finish/1", headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "選択されたTodoは存在しません"}


def test_finish_todo_already_finished(client, get_headers):
    """ 既に終了したTodoを終了しようとした場合 """
    setup_create_todo(client, get_headers)
    setup_finish_todo(client, get_headers)
    response = client.put("/todos/finish/1", headers=get_headers)
    assert response.status_code == 409
    assert response.json() == {"detail": "既に終了したTodoです"}


def test_finish_todos(client, get_headers):
    for _ in range(2):
        setup_create_todo(client, get_headers)
    data = {"ids": [1, 2]}
    response = client.put("todos/multi/finish", json=data, headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": "2件のTodoを終了しました",
        "titles": f"{test_title}\n{test_title}"
    }


def test_finish_todos_with_finished_todo(client, get_headers):
    """ 既に終了したTodoを含む状態で複数Todoの一括終了 """
    for _ in range(2):
        setup_create_todo(client, get_headers)
    setup_finish_todo(client, get_headers)
    response = client.get("/todos", headers=get_headers)
    print(response.json())
    data = {"ids": [1, 2]}
    response = client.put("todos/multi/finish", json=data, headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": "登録のない/削除済みTodoが含まれているため、一部のTodo終了処理をスキップしました\n1件のTodoを終了しました",
        "titles": f"{test_title}"
    }


def test_finish_todos_not_exist(client, get_headers):
    """ 存在しないTodoを複数終了しようとした場合 """
    data = {"ids": [1, 2]}
    response = client.put("todos/multi/finish", json=data, headers=get_headers)
    assert response.status_code == 409
    assert response.json() == {
        "detail": "終了リクエストされたTodoは全て存在しないか、既に終了しています"
    }
