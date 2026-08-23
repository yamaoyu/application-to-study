TEST_TITLE = "create test"
TEST_DUE = "2024-11-10"
TEST_DETAIL = "detail"


def setup_create_todo(client, get_resource_owner_headers):
    data = {
        "todos": [{"title": TEST_TITLE, "due": TEST_DUE, "detail": TEST_DETAIL}]
    }
    client.post("/todos/bulk-create", json=data, headers=get_resource_owner_headers)


def setup_finish_todo(client, get_resource_owner_headers):
    data = {"ids": [1]}
    client.patch("/todos/bulk-finish", json=data, headers=get_resource_owner_headers)
