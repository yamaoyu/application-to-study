from app.error_codes import NotFoundCode
from helpers.todo import TEST_TITLE, setup_create_todo


def test_delete_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1]}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
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
    response = client.post("/todos/bulk-delete", json=data, headers=user2_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "todo_id": 1,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            }
        ]
    }


def test_delete_todo_not_exist(client, get_resource_owner_headers):
    """ 存在しないTodoを削除しようとした場合 """
    data = {"ids": [1]}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "todo_id": 1,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            }
        ]
    }


def test_delete_todo_with_duplicate_ids(client, get_resource_owner_headers):
    """ 同じTodo IDを複数回指定して削除しようとした場合、重複は排除される """
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 1]}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_delete_todos(client, get_resource_owner_headers):
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 2,
        "error_count": 0,
        "results": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "result": "success",
                "reason": None
            },
            {
                "todo_id": 2,
                "title": TEST_TITLE,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_delete_todos_one_not_found(client, get_resource_owner_headers):
    """ 2つのTodoの削除、うち1つは存在しない """
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 1,
        "results": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "result": "success",
                "reason": None
            },
            {
                "todo_id": 2,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            }
        ]
    }


def test_delete_todos_not_exist(client, get_resource_owner_headers):
    """ 存在しないTodoを複数削除しようとした場合 """
    data = {"ids": [1, 2]}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 2,
        "results": [
            {
                "todo_id": 1,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            },
            {
                "todo_id": 2,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            }
        ]
    }


def test_delete_todos_with_empty_list(client, get_resource_owner_headers):
    """ 空のTodo IDリストで削除しようとした場合 """
    data = {"ids": []}
    response = client.post("/todos/bulk-delete", json=data, headers=get_resource_owner_headers)
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
