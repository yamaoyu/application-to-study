from app.error_codes import NotFoundCode, ConflictCode
from test.helpers.todo import TEST_TITLE, setup_create_todo, setup_finish_todo


def test_finish_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
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


def test_finish_todo_before_create_todo(client, get_resource_owner_headers):
    """ 登録されていないTodoを終了しようとした場合 """
    data = {"ids": [1]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
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


def test_finish_already_finished_todo(client, get_resource_owner_headers):
    """ 既に終了したTodoのみを終了しようとした場合 """
    setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {"ids": [1]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "result": "error",
                "reason": ConflictCode.TODO_ALREADY_FINISHED
            }
        ]
    }


def test_finish_todos(client, get_resource_owner_headers):
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
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


def test_finish_todos_with_duplicate_ids(client, get_resource_owner_headers):
    """ 同じTodoを複数個終了しようとした場合、重複排除される """
    setup_create_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 1]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
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


def test_finish_todos_with_finished_todo(client, get_resource_owner_headers):
    """ 既に終了したTodoを含む状態で複数Todoの一括終了 """
    for _ in range(2):
        setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {"ids": [1, 2]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 1,
        "results": [
            {
                "todo_id": 1,
                "title": TEST_TITLE,
                "result": "error",
                "reason": ConflictCode.TODO_ALREADY_FINISHED
            },
            {
                "todo_id": 2,
                "title": TEST_TITLE,
                "result": "success",
                "reason": None
            }
        ]
    }


def test_finish_todos_not_exist(client, get_resource_owner_headers):
    """ 存在しないTodoを複数終了しようとした場合 """
    data = {"ids": [1, 2]}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
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


def test_finish_todos_with_empty_list(client, get_resource_owner_headers):
    """ リクエストされたTodoリストが空の場合 """
    data = {"ids": []}
    response = client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
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
