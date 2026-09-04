from app.error_codes import NotFoundCode, ConflictCode
from app.domain.todo.exceptions import TodoValidationReason
from helpers.todo import TEST_TITLE, TEST_DUE, TEST_DETAIL, setup_create_todo, setup_finish_todo


def test_create_todo(client, get_resource_owner_headers):
    " todoを1つ作成 "
    data = {
        "todos": [{"title": TEST_TITLE, "due": TEST_DUE, "detail": TEST_DETAIL}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "title": TEST_TITLE,
                "due": TEST_DUE,
                "detail": TEST_DETAIL,
                "reason": None,
                "result": "success"
            }
        ]
    }


def test_create_todo_with_invalid_date(client, get_resource_owner_headers):
    """ todoを1つ作成、存在しない日付の場合 """
    data = {
        "todos": [{"title": TEST_TITLE, "due": "2026-6-31"}]
    }
    response = client.post("/todos/bulk-create",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "title": TEST_TITLE,
                "due": "2026-6-31",
                "detail": "",
                "reason": TodoValidationReason.INVALID_DUE,
                "result": "error"
            }
        ]
    }


def test_create_todos(client, get_resource_owner_headers):
    """ todoを複数作成 """
    data = {
        "todos": [{"title": TEST_TITLE, "due": TEST_DUE, "detail": TEST_DETAIL},
                  {"title": TEST_TITLE + "2", "due": TEST_DUE, "detail": TEST_DETAIL + "2"}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 2,
        "error_count": 0,
        "results": [
            {
                "title": TEST_TITLE,
                "due": TEST_DUE,
                "detail": TEST_DETAIL,
                "reason": None,
                "result": "success"
            },
            {
                "title": TEST_TITLE + "2",
                "due": TEST_DUE,
                "detail": TEST_DETAIL + "2",
                "reason": None,
                "result": "success"
            }
        ]
    }


def test_create_todos_with_invalid_date(client, get_resource_owner_headers):
    " todoを複数作成、うち1つは不正な日付 "
    data = {
        "todos": [{"title": TEST_TITLE, "due": TEST_DUE, "detail": TEST_DETAIL},
                  {"title": TEST_TITLE + "2", "due": "2026-6-31", "detail": TEST_DETAIL + "2"}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 1,
        "results": [
            {
                "title": TEST_TITLE,
                "due": TEST_DUE,
                "detail": TEST_DETAIL,
                "reason": None,
                "result": "success"
            },
            {
                "title": TEST_TITLE + "2",
                "due": "2026-6-31",
                "detail": TEST_DETAIL + "2",
                "reason": TodoValidationReason.INVALID_DUE,
                "result": "error"
            }
        ]
    }


def test_fail_create_todos_with_long_title(client, get_resource_owner_headers):
    """ titleは32文字まで、32文字を超える場合はエラー """
    data = {
        "todos": [{"title": "a" * 33, "due": TEST_DUE, "detail": TEST_DETAIL}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "title": "a" * 33,
                "due": TEST_DUE,
                "detail": TEST_DETAIL,
                "reason": TodoValidationReason.TITLE_TOO_LONG,
                "result": "error"
            }
        ]
    }


def test_fail_create_todos_without_title(client, get_resource_owner_headers):
    """ titleが含まれない場合はエラー """
    data = {
        "todos": [{"due": TEST_DUE, "detail": TEST_DETAIL}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "title": "",
                "due": TEST_DUE,
                "detail": TEST_DETAIL,
                "reason": TodoValidationReason.TITLE_REQUIRED,
                "result": "error"
            }
        ]
    }


def test_fail_create_todos_without_due(client, get_resource_owner_headers):
    """ dueが存在しない場合はエラー """
    data = {
        "todos": [{"title": TEST_TITLE, "detail": TEST_DETAIL}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "title": TEST_TITLE,
                "due": "",
                "detail": TEST_DETAIL,
                "reason": TodoValidationReason.DUE_REQUIRED,
                "result": "error"
            }
        ]
    }


def test_fail_create_todos_with_long_detail(client, get_resource_owner_headers):
    """ detailは200文字まで、200文字を超える場合はエラー """
    data = {
        "todos": [{"title": TEST_TITLE, "due": TEST_DUE, "detail": "a" * 201}]
    }
    response = client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "title": TEST_TITLE,
                "due": TEST_DUE,
                "detail": "a" * 201,
                "reason": TodoValidationReason.DETAIL_TOO_LONG,
                "result": "error"
            }
        ]
    }


def test_edit_todo(client, get_resource_owner_headers):
    setup_create_todo(client, get_resource_owner_headers)
    data = {"title": "new title", "due": "2024-11-11", "detail": "new detail"}
    response = client.patch("/todos/update/1", json=data, headers=get_resource_owner_headers)
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


def test_edit_not_exist_todo(client, get_resource_owner_headers):
    """ 存在しないTodoを更新しようとした場合 """
    data = {"title": "new title", "due": "2024-11-11", "detail": "new detail"}
    response = client.patch("/todos/update/1", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_edit_todo_by_another_user(client, get_resource_owner_headers, get_non_resource_owner_headers):
    """ 他のユーザーが作成したTodoを更新した場合 """
    setup_create_todo(client, get_resource_owner_headers)
    user2_headers = get_non_resource_owner_headers
    data = {"title": "new title", "due": TEST_DUE, "detail": TEST_DETAIL}
    response = client.patch("/todos/update/1", json=data, headers=user2_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.TODO_NOT_FOUND
    }


def test_fail_edit_completed_todo(client, get_resource_owner_headers):
    """ 完了済みTodoを更新しようとした場合 """
    setup_create_todo(client, get_resource_owner_headers)
    setup_finish_todo(client, get_resource_owner_headers)
    data = {"title": "new title", "due": TEST_DUE, "detail": TEST_DETAIL}
    response = client.patch("/todos/update/1", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 409
    assert response.json() == {
        "code": ConflictCode.TODO_ALREADY_FINISHED
    }
