from unittest.mock import patch
from datetime import timedelta
from testdata import RESOURCE_OWNER_USERNAME
from lib.security import create_access_token
from app.error_codes import NotFoundCode, NotAuthorizedCode
from helpers.todo import TEST_TITLE, TEST_DUE, TEST_DETAIL, setup_create_todo, setup_finish_todo


def test_get_all_todos(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    response = client.get("/todos", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "status": False,
                "due": TEST_DUE,
                "detail": TEST_DETAIL
            }
        ]
    }


def test_get_todos_filter_by_status(client, get_resource_owner_headers):
    """ ステータスで活動を絞って取得 """
    data = {
        "todos": [{"title": TEST_TITLE, "due": TEST_DUE, "detail": TEST_DETAIL},
                  {"title": TEST_TITLE + "2", "due": TEST_DUE, "detail": TEST_DETAIL + "2"}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    # 1つ目のTodoを終了する
    setup_finish_todo(client, get_resource_owner_headers)
    assert response.status_code == 200
    # ステータスで絞って検索
    # 終了したTodoのみを取得
    response = client.get("/todos?status=true", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "due": TEST_DUE,
                "detail": TEST_DETAIL,
                "status": True
            }
        ]
    }
    # 終了していないTodoのみを取得
    response = client.get("/todos?status=false", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "todo_id": 2,
                "title": TEST_TITLE + "2",
                "due": TEST_DUE,
                "detail": TEST_DETAIL + "2",
                "status": False
            }
        ]
    }


def test_get_todos_filter_by_due(client, get_resource_owner_headers):
    """ 期限でTodoを絞って取得 """
    data = {
        "todos": [{"title": TEST_TITLE, "due": "2026-07-31", "detail": TEST_DETAIL},
                  {"title": TEST_TITLE + "2", "due": "2026-08-01", "detail": TEST_DETAIL + "2"}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    # 期限が2026/8/1以降のTodoを取得
    response = client.get("/todos?start_due=2026/8/1",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "todo_id": 2,
                "title": TEST_TITLE + "2",
                "due": "2026-08-01",
                "detail": TEST_DETAIL + "2",
                "status": False
            }
        ]
    }
    # 期限が2026/7/31以前のTodoを取得
    response = client.get("/todos?end_due=2026/7/31",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "due": "2026-07-31",
                "detail": TEST_DETAIL,
                "status": False
            }
        ]
    }


def test_get_todos_filter_by_title(client, get_resource_owner_headers):
    """ タイトルでTodoを絞って取得 """
    data = {
        "todos": [{"title": TEST_TITLE, "due": "2026-07-31", "detail": TEST_DETAIL},
                  {"title": "aaa", "due": "2026-08-01", "detail": TEST_DETAIL + "2"}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    # タイトルに"test"を含むTodoを取得
    response = client.get("/todos?title=test",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "due": "2026-07-31",
                "detail": TEST_DETAIL,
                "status": False
            }
        ]
    }


def test_get_all_incomplete_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {
        "todos": [{"title": "test_2", "due": TEST_DUE, "detail": TEST_DETAIL}]
    }
    client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    response = client.get("/todos?status=False", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [{"todo_id": 2,
                   "title": "test_2",
                   "status": False,
                   "due": TEST_DUE,
                   "detail": TEST_DETAIL}]
    }


def test_get_complete_todo(client, get_resource_owner_headers):
    """ 終了したTodoのみを取得 """
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    client.post("/todos", json={}, headers=get_resource_owner_headers)
    response = client.get("/todos?status=True", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [{"todo_id": 1,
                   "title": "create test",
                   "status": True,
                   "due": TEST_DUE,
                   "detail": TEST_DETAIL}]
    }


def test_get_todo_with_expired_token(client, get_resource_owner_headers):
    """ 期限の切れたトークンでTodoを取得しようとした場合 """
    def mock_create_expired_access_token(data, minutes):
        expires_delta = timedelta(minutes=minutes)
        return create_access_token(data, expires_delta)

    setup_create_todo(client, get_resource_owner_headers)
    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": RESOURCE_OWNER_USERNAME},
                                                        minutes=-30)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/todos", headers=headers)
        assert response.status_code == 401
        assert response.json() == {
            "code": NotAuthorizedCode.NOT_AUTHORIZED
        }


def test_get_all_todo_without_register(client, get_resource_owner_headers):
    """ 作成したTodoが1つもない状態でget """
    response = client.get("/todos", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": []
    }


def test_get_todo_by_id(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    response = client.get("/todos/1", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"todo_id": 1,
                               "title": TEST_TITLE,
                               "status": False,
                               "due": TEST_DUE,
                               "detail": TEST_DETAIL}


def test_get_todo_by_another_user(client, get_resource_owner_headers, get_non_resource_owner_headers):
    """ 他のユーザーが作成したTodoの取得はできない """
    setup_create_todo(client, get_resource_owner_headers)
    user2_headers = get_non_resource_owner_headers
    response = client.get("/todos/1", headers=user2_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }
