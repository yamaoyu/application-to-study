from unittest.mock import patch
from datetime import timedelta
from testdata import RESOURCE_OWNER_USERNAME
from lib.security import create_access_token
from app.error_codes import NotFoundCode, NotAuthorizedCode, ConflictCode

test_title = "create test"
test_due = "2024-11-10"
test_detail = "detail"


def setup_create_todo(client, get_resource_owner_headers):
    data = {
        "todos": [{"title": test_title, "due": test_due, "detail": test_detail}]
    }
    client.post("/todos", json=data, headers=get_resource_owner_headers)


def setup_finish_todo(client, get_resource_owner_headers):
    data = {"ids": [1]}
    client.put("/todos/finish", json=data, headers=get_resource_owner_headers)


def test_create_todo(client, get_resource_owner_headers):
    data = {
        "todos": [{"title": test_title, "due": test_due, "detail": test_detail}]
    }
    response = client.post("/todos", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "reason": None,
                "result": "success"
            }
        ]
    }


def test_create_todos(client, get_resource_owner_headers):
    data = {
        "todos": [{"title": test_title, "due": test_due, "detail": test_detail},
                  {"title": test_title + "2", "due": test_due, "detail": test_detail + "2"}]
    }
    response = client.post("/todos", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "success_count": 2,
        "error_count": 0,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "reason": None,
                "result": "success"
            },
            {
                "title": test_title + "2",
                "due": test_due,
                "detail": test_detail + "2",
                "reason": None,
                "result": "success"
            }
        ]
    }


def test_get_all_todos(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    response = client.get("/todos", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == [{"todo_id": 1,
                                "title": test_title,
                                "status": False,
                                "due": test_due,
                                "detail": test_detail}]


def test_get_todos_with_query_parameters(client, get_resource_owner_headers):
    """ クエリパラメータで活動を絞って取得 """
    setup_create_todo(client, get_resource_owner_headers)
    # ステータスで絞る
    response = client.get("/todos?status=false", headers=get_resource_owner_headers)
    assert response.status_code == 200
    # 期限で絞る(期限外は表示されない)
    response = client.get("/todos?status=false&start_due=2024/11/11",
                          headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_get_all_incomplete_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {
        "todos": [{"title": "test_2", "due": test_due, "detail": test_detail}]
    }
    client.post("/todos", json=data, headers=get_resource_owner_headers)
    response = client.get("/todos?status=False", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == [{"todo_id": 2,
                                "title": "test_2",
                                "status": False,
                                "due": test_due,
                                "detail": test_detail}]


def test_create_todo_with_invalid_date(client, get_resource_owner_headers):
    """ 存在しない日付の場合 """
    data = {
        "todos": [{"title": test_title, "due": "2024-6-31"}]
    }
    response = client.post("/todos",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_DATE",
                "field": "due"
            }
        ]
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
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_get_specific_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    response = client.get("/todos/1", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"todo_id": 1,
                               "title": test_title,
                               "status": False,
                               "due": test_due,
                               "detail": test_detail}


def test_get_todo_by_another_user(client, get_resource_owner_headers, get_non_resource_owner_headers):
    """ 他のユーザーが作成したTodoの取得はできない """
    setup_create_todo(client, get_resource_owner_headers)
    user2_headers = get_non_resource_owner_headers
    response = client.get("/todos/1", headers=user2_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_delete_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1]}
    response = client.put("/todos/delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_delete_todo_by_another_user(client, get_resource_owner_headers, get_non_resource_owner_headers):
    """ 他のユーザーが作成したTodoを削除しようとする """
    setup_create_todo(client, get_resource_owner_headers)
    user2_headers = get_non_resource_owner_headers
    data = {"ids": [1]}
    response = client.put("/todos/delete", json=data, headers=user2_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_delete_todo_not_exist(client, get_resource_owner_headers):
    """ 存在しないTodoを削除しようとした場合 """
    data = {"ids": [1]}
    response = client.put("/todos/delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_delete_todos(client, get_resource_owner_headers):
    """ 複数Todoの一括削除で一部のTodoが存在しない場合 """
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.put("/todos/delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 2,
        "error_count": 0,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            },
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_delete_todos_not_exist(client, get_resource_owner_headers):
    """ 存在しないTodoを複数削除しようとした場合 """
    data = {"ids": [1, 2]}
    response = client.put("/todos/delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_delete_todos_empty(client, get_resource_owner_headers):
    """ 空のTodo IDリストで削除しようとした場合 """
    data = {"ids": []}
    response = client.put("/todos/delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "EMPTY_LIST",
                "field": "ids"
            }
        ]
    }


def test_edit_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    data = {"title": "new title", "due": "2024-11-11", "detail": "new detail"}
    response = client.put("/todos/update/1", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "title": "new title",
                "due": "2024-11-11",
                "detail": "new detail",
                "result": "success",
                "reason": None
            }
        ]
    }


def test_edit_todo_by_another_user(client, get_resource_owner_headers, get_non_resource_owner_headers):
    """ 他のユーザーが作成したTodoを更新した場合 """
    setup_create_todo(client, get_resource_owner_headers)
    user2_headers = get_non_resource_owner_headers
    data = {"title": "new title", "due": test_due, "detail": test_detail}
    response = client.put("/todos/update/1", json=data, headers=user2_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_finish_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1]}
    response = client.put("/todos/finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_finish_todo_before_create_todo(client, get_resource_owner_headers):
    """ 登録されていないTodoを終了しようとした場合 """
    data = {"ids": [1]}
    response = client.put("/todos/finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_finish_already_finished_todo(client, get_resource_owner_headers):
    """ 既に終了したTodoのみを終了しようとした場合 """
    setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {"ids": [1]}
    response = client.put("/todos/finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 409
    assert response.json() == {
        "code": ConflictCode.TODO_ALREADY_FINISHED
    }


def test_finish_todos(client, get_resource_owner_headers):
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.put("/todos/finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 2,
        "error_count": 0,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            },
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_finish_todos_with_finished_todo(client, get_resource_owner_headers):
    """ 既に終了したTodoを含む状態で複数Todoの一括終了 """
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.put("/todos/finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 1,
        "results": [
            {
                "title": test_title,
                "due": test_due,
                "detail": test_detail,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_finish_todos_not_exist(client, get_resource_owner_headers):
    """ 存在しないTodoを複数終了しようとした場合 """
    data = {"ids": [1, 2]}
    response = client.put("/todos/finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }
