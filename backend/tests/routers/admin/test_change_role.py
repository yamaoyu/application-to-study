import pytest
from datetime import datetime
from db.db_model import User
from app.error_codes import ConflictCode, NotFoundCode, NotAuthorizedCode
from tests.testdata import ADMIN_USERNAME
from app.security.password import get_password_hash

GENERAL_ACTIVE = "general-active"
GENERAL_SUSPEND = "general-suspend"
ADMIN_ACTIVE = "admin-active"
ADMIN_SUSPEND = "admin-suspend"
PLAIN_PASSWORD = "dummy-Password1"
HASHED_PASSWORD = get_password_hash(PLAIN_PASSWORD)


@pytest.fixture
def setup_users(db_session):
    now = datetime.now()
    users = [
        User(
            username=GENERAL_ACTIVE,
            password=HASHED_PASSWORD,
            status="active",
            role="general",
            created_at=now,
            last_active_at=now,
        ),
        User(
            username=GENERAL_SUSPEND,
            password=HASHED_PASSWORD,
            status="suspended",
            role="general",
            created_at=now,
            last_active_at=now
        ),
        User(
            username=ADMIN_ACTIVE,
            password=HASHED_PASSWORD,
            status="active",
            role="admin",
            created_at=now,
            last_active_at=now
        ),
        User(
            username=ADMIN_SUSPEND,
            password=HASHED_PASSWORD,
            status="suspended",
            role="admin",
            created_at=now,
            last_active_at=now
        )
    ]

    db_session.add_all(users)
    db_session.commit()

    return users


def login(client, username: str, password: str):
    login_info = {"username": username, "password": password}
    token = client.post("/login", json=login_info)
    access_token = token.json()['access_token']
    return {"Authorization": f"Bearer {access_token}"}


def test_change_user_role_general_to_admin(client, get_admin_headers, setup_users):
    data = {
        "role": "admin"
    }
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data,
                            headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "username": GENERAL_ACTIVE,
        "role": "admin"
    }


def test_change_user_role_admin_to_general(client, get_admin_headers, setup_users):
    data = {
        "role": "general"
    }
    response = client.patch(f"/admin/users/{ADMIN_ACTIVE}/role",
                            json=data,
                            headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "username": ADMIN_ACTIVE,
        "role": "general"
    }


def test_general_user_fail_to_change_role(client, get_resource_owner_headers, setup_users):
    data = {
        "role": "admin"
    }
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_HAVE_PERMISSION
    }


def test_fail_when_not_acceptable_role(client, get_admin_headers, setup_users):
    data = {
        "role": "INVALID"
    }
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data,
                            headers=get_admin_headers)
    assert response.status_code == 422
    assert response.json() == {
        'code': 'VALIDATION_ERROR',
        'errors': [
            {
                'field': 'role',
                'code': 'INVALID_INPUT',
            },
        ],
    }


def test_fail_change_not_existing_user_role(client, get_admin_headers, setup_users):
    data = {
        "role": "admin"
    }
    response = client.patch("/admin/users/not-exists/role",
                            json=data,
                            headers=get_admin_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.USER_NOT_FOUND
    }


def test_change_status_with_same_status(client, get_admin_headers, setup_users):
    "現在と同じステータスを指定されても成功とする"
    data = {
        "role": "general"
    }
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data,
                            headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "username": GENERAL_ACTIVE,
        "role": "general"
    }


def test_fail_change_last_admin_to_general(client, get_admin_headers, setup_users):
    data = {
        "role": "general"
    }
    client.patch(f"/admin/users/{ADMIN_ACTIVE}/role",
                 json=data,
                 headers=get_admin_headers)
    # テストDBにはADMIN_USERNAMEしかadminユーザーがないはず
    response = client.patch(f"/admin/users/{ADMIN_USERNAME}/role",
                            json=data,
                            headers=get_admin_headers)
    assert response.status_code == 409
    assert response.json() == {
        "code": ConflictCode.LAST_ADMIN_USER
    }


def test_user_denied_admin_feature_after_role_changed_to_general(client, get_admin_headers, setup_users):
    data_before_change_role = {
        "role": "general"
    }
    logged_in_headers = login(client, ADMIN_ACTIVE, PLAIN_PASSWORD)
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data_before_change_role,
                            headers=logged_in_headers)
    assert response.status_code == 200
    assert response.json() == {
        "username": GENERAL_ACTIVE,
        "role": "general"
    }

    client.patch(
        f"/admin/users/{ADMIN_ACTIVE}/role",
        json=data_before_change_role,
        headers=get_admin_headers
    )
    headers = login(client, ADMIN_ACTIVE, PLAIN_PASSWORD)
    data_after_change_role = {
        "role": "admin"
    }
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data_after_change_role,
                            headers=headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_HAVE_PERMISSION
    }


def test_user_accepted_admin_feature_after_role_changed_to_admin(client, get_admin_headers, setup_users):
    data_before_change_role = {
        "role": "admin"
    }
    logged_in_headers = login(client, GENERAL_ACTIVE, PLAIN_PASSWORD)
    response = client.patch("/admin/users/not-exists/role",
                            json=data_before_change_role,
                            headers=logged_in_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_HAVE_PERMISSION
    }
    client.patch(
        f"/admin/users/{GENERAL_ACTIVE}/role",
        json=data_before_change_role,
        headers=get_admin_headers
    )
    logged_in_headers = login(client, GENERAL_ACTIVE, PLAIN_PASSWORD)
    data_after_change_role = {
        "role": "general"
    }
    response = client.patch(f"/admin/users/{ADMIN_ACTIVE}/role",
                            json=data_after_change_role,
                            headers=logged_in_headers)
    assert response.status_code == 200
    assert response.json() == {
        "username": ADMIN_ACTIVE,
        "role": "general"
    }


def test_suspended_user_cannot_change_role(client, get_suspended_user_headers, setup_users):
    data = {
        "role": "admin"
    }
    response = client.patch(f"/admin/users/{GENERAL_ACTIVE}/role",
                            json=data,
                            headers=get_suspended_user_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.USER_SUSPENDED
    }
