import pytest
from conftest import SECRET_KEY, ALGORITHM
from testdata import RESOURCE_OWNER_USERNAME, RESOURCE_OWNER_PLAIN_PASSWORD, ADMIN_PASSWORD
from jose import jwt
from jose.exceptions import JWTError
from app.error_codes import NotAuthorizedCode, ConflictCode

# conftestで登録したユーザーとは別にこのファイルでユーザー作成する際に使うパスワード
password = "P@ssword1"


def test_register_user(client):
    user_info = {"username": "test",
                 "password": password}
    response = client.post("/users", json=user_info)
    assert response.status_code == 201
    assert response.json() == {
        "username": "test",
        "password": "*********",
        "email": None,
        "role": "general"
    }


def test_register_user_with_short_username(client):
    """3文字以上、16文字以下でないユーザー名で登録した場合"""
    user_info = {"username": "t",
                 "password": password}
    response = client.post("/users", json=user_info)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_USERNAME",
                "field": "username"
            }
        ]
    }


def test_register_user_with_invalid_password(client):
    """8文字以上、16文字以下でないパスワードで登録した場合"""
    user_info = {"username": "test",
                 "password": "test"}
    response = client.post("/users", json=user_info)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_PASSWORD",
                "field": "password"
            }
        ]
    }


def test_register_user_with_invalid_email(client):
    """「@」が含まれないメールアドレスを登録した場合"""
    user_info = {"username": "test",
                 "password": password,
                 "email": "aaaaa"}
    response = client.post("/users", json=user_info)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_EMAIL",
                "field": "email"
            }
        ]
    }


def test_register_with_duplicate_user_name(client, create_resource_owner):
    """ 既に登録されているユーザー名で登録した場合 """
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    response = client.post("/users", json=user_info)
    assert response.status_code == 409
    assert response.json() == {
        "code": ConflictCode.USER_ALREADY_EXISTS
    }


def test_login(client, create_resource_owner):
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
    assert len(response.json()) == 3
    assert response.json()["role"] == "general"

    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] is not None
    assert len(response.cookies["refresh_token"]) >= 100

    assert "device_id" in response.cookies
    assert response.cookies["device_id"] is not None
    # 作成されるトークンは最低100文字
    assert len(access_token) >= 100
    try:
        decoded_token = jwt.decode(
            access_token, SECRET_KEY, ALGORITHM)
        assert "sub" in decoded_token
        assert decoded_token["sub"] == "testuser"
    except JWTError as e:
        pytest.fail(f"Invalid JWT token {str(e)}")


def test_login_with_form_data_for_swagger_ui(client, create_resource_owner):
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    response = client.post("/login", data=user_info)
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
    assert "access_token" in response.json()


def test_login_with_invalid_password(client, create_resource_owner):
    """パスワードを間違えた場合"""
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": "invalid_password"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 401
    assert response.json() == {
        "code": NotAuthorizedCode.LOGIN_FAILED
    }


def test_login_not_registered_user(client):
    """登録されていないユーザーでログイン"""
    user_info = {"username": "test",
                 "password": password}
    response = client.post("/login", json=user_info)
    assert response.status_code == 401
    assert response.json() == {
        "code": NotAuthorizedCode.LOGIN_FAILED
    }


def test_logout(client, get_resource_owner_headers):
    response = client.post("/logout", headers=get_resource_owner_headers)
    assert response.status_code == 200
    response = client.post("/token", headers=get_resource_owner_headers)
    assert response.status_code == 401


def test_regenerate_token(client, get_resource_owner_headers):
    response = client.post("/token", headers=get_resource_owner_headers)
    access_token = response.json()["access_token"]
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
    assert len(access_token) >= 100
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
        assert "sub" in decoded_token
        assert decoded_token["sub"] == "testuser"
    except JWTError as e:
        pytest.fail(f"Invalid JWT token {str(e)}")


def test_regenerate_token_fail_without_cookie(client, get_resource_owner_headers):
    client.cookies.clear()
    response = client.post("/token", headers=get_resource_owner_headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_AUTHORIZED
    }


def test_regenerate_token_with_invalid_refresh_token(client, get_resource_owner_headers):
    client.cookies.set("refresh_token", "invalid_refresh_token")
    response = client.post("/token", headers=get_resource_owner_headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_AUTHORIZED
    }


def test_regenerate_token_with_invalid_device_id(client, get_resource_owner_headers):
    client.cookies.set("device_id", "device_id")
    response = client.post("/token", headers=get_resource_owner_headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_AUTHORIZED
    }


def test_change_password(client, get_resource_owner_headers):
    new_password = "newP@ssword1"
    data = {
        "old_password": RESOURCE_OWNER_PLAIN_PASSWORD,
        "new_password": new_password
    }
    response = client.patch("/password", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200


def login_fail_after_test_change_password_with(client, get_resource_owner_headers):
    new_password = "newP@ssword1"
    data = {
        "old_password": RESOURCE_OWNER_PLAIN_PASSWORD,
        "new_password": new_password
    }
    response = client.patch("/password", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    response = client.post("/login", json=user_info)
    assert response.status_code == 401


def test_change_password_with_invalid_old_password(client, get_resource_owner_headers):
    new_password = "newP@ssword1"
    data = {
        "old_password": new_password,
        "new_password": new_password
    }
    response = client.patch("/password", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": NotAuthorizedCode.INVALID_CURRENT_PASSWORD
    }


def test_change_password_with_invalid_password(client, get_resource_owner_headers):
    new_password = "invalid"
    data = {
        "old_password": RESOURCE_OWNER_PLAIN_PASSWORD,
        "new_password": new_password
    }
    response = client.patch("/password", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_PASSWORD",
                "field": "new_password"
            }
        ]
    }


def test_admin_user_can_create_admin_user(client, get_admin_headers):
    user_info = {"username": "admin2",
                 "password": ADMIN_PASSWORD}
    response = client.post("/admins", json=user_info, headers=get_admin_headers)
    assert response.status_code == 201
    assert response.json() == {
        "username": "admin2",
        "password": "*********",
        "email": None,
        "role": "admin"
    }


def test_general_user_fail_to_access_admin_page(client, get_resource_owner_headers):
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    response = client.post("/admins", json=user_info, headers=get_resource_owner_headers)
    assert response.status_code == 403
