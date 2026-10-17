import pytest
from datetime import timedelta, datetime
from db.db_model import User
from unittest.mock import patch
from app.error_codes import NotAuthorizedCode, NotFoundCode
from testdata import ADMIN_USERNAME, ADMIN_PASSWORD


@pytest.fixture
def users_for_filter_test(db_session):
    now = datetime.now()
    users = [
        User(
            username="general-active",
            password="dummy-Password1",
            status="active",
            role="general",
            created_at=now,
            last_active_at=now,
            must_change_password=False
        ),
        User(
            username="general-suspend",
            password="dummy-Password1",
            status="suspended",
            role="general",
            created_at=now,
            last_active_at=now,
            must_change_password=False
        ),
        User(
            username="admin-active",
            password="dummy-Password1",
            status="active",
            role="admin",
            created_at=now,
            last_active_at=now,
            must_change_password=False
        ),
        User(
            username="admin-suspend",
            password="dummy-Password1",
            status="suspended",
            role="admin",
            created_at=now,
            last_active_at=now,
            must_change_password=False
        ),
        User(
            username="for-date-filter",
            password="dummy-Password1",
            status="active",
            role="general",
            created_at=now - timedelta(days=1),
            last_active_at=now + timedelta(days=1),
            must_change_password=False
        )
    ]

    db_session.add_all(users)
    db_session.commit()

    return users


def test_get_users_without_filter(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0


def test_get_users_filter_with_role(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users?role=admin", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(user["role"] == "admin" for user in response.json()["users"])


def test_get_users_filter_with_status(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users?status=active", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(user["status"] == "active" for user in response.json()["users"])


def test_get_users_filter_with_role_and_status(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users?role=admin&status=active", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(user["role"] == "admin" and user["status"] == "active"
               for user in response.json()["users"])


def test_get_users_with_partial_username(client, get_admin_headers, users_for_filter_test):
    # 名前は部分一致で検索している
    response = client.get("/admin/users?username=general", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(
        "general" in user["username"] for user in response.json()["users"])


def test_get_users_with_exact_username(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users?username=general-active", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(
        user["username"] == "general-active" for user in response.json()["users"])


def test_get_users_with_last_active_at(client, get_admin_headers, users_for_filter_test):
    last_active_at = users_for_filter_test[0].last_active_at.isoformat()
    response = client.get(
        f"/admin/users?last_active_at={last_active_at}", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(
        datetime.fromisoformat(user["last_active_at"]) >= datetime.fromisoformat(last_active_at)
        for user in response.json()["users"]
    )


def test_get_users_with_created_at(client, get_admin_headers, users_for_filter_test):
    created_at = users_for_filter_test[0].created_at.isoformat()
    response = client.get(
        f"/admin/users?created_at={created_at}", headers=get_admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) > 0
    assert all(
        datetime.fromisoformat(user["created_at"]) >= datetime.fromisoformat(created_at)
        for user in response.json()["users"]
    )


def test_get_users_by_general_user(client, get_resource_owner_headers):
    response = client.get("/admin/users", headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": "NOT_HAVE_PERMISSION"
    }


def test_get_users_with_invalid_status(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users?status=invalid", headers=get_admin_headers)
    assert response.status_code == 422
    assert response.json() == {
        'code': 'VALIDATION_ERROR',
        "errors": [
            {
                'field': 'status',
                'code': 'INVALID_INPUT'
            }
        ]
    }


def test_get_users_with_invalid_role(client, get_admin_headers, users_for_filter_test):
    response = client.get("/admin/users?role=invalid", headers=get_admin_headers)
    assert response.status_code == 422
    assert response.json() == {
        'code': 'VALIDATION_ERROR',
        "errors": [
            {
                'field': 'role',
                'code': 'INVALID_INPUT'
            }
        ]
    }


def test_suspended_user_cannot_get_users(client, get_suspended_user_headers):
    response = client.get("/admin/users", headers=get_suspended_user_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.USER_SUSPENDED
    }


def test_must_change_password_user_denied(client, get_admin_headers):
    response = client.patch(
        f"/admin/users/{ADMIN_USERNAME}/password", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json()["password"] != ADMIN_PASSWORD
    new_password = response.json()["password"]
    user_info = {"username": ADMIN_USERNAME,
                 "password": new_password}
    response = client.post("/login", json=user_info)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    token_type = response.json()["token_type"]
    response = client.get("/admin/users", headers={"Authorization": f"{token_type} {access_token}"})
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.PASSWORD_CHANGE_REQUIRED
    }


def test_get_users_without_macth_users(client, get_admin_headers):
    # 存在しないユーザーを検索したいが、テスト用ユーザーが存在するため、モックを使って、ユーザーが存在しない場合の挙動をテストする
    def mock_get_users(self,
                       status=None,
                       last_active_at=None,
                       created_at=None,
                       role=None,
                       username=None):
        return []
    with patch("app.repositories.user_repository.UserRepository.get_users", mock_get_users):
        response = client.get("/admin/users", headers=get_admin_headers)
        assert response.status_code == 404
        assert response.json() == {
            "code": NotFoundCode.USER_NOT_FOUND
        }
