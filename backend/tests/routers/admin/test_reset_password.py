from testdata import RESOURCE_OWNER_USERNAME, RESOURCE_OWNER_PLAIN_PASSWORD, ADMIN_USERNAME
from app.error_codes import NotAuthorizedCode, NotFoundCode


def test_reset_password(client, get_admin_headers, create_resource_owner):
    password_change_response = client.patch(
        f"/admin/users/{RESOURCE_OWNER_USERNAME}/password", headers=get_admin_headers)
    assert password_change_response.status_code == 200
    assert password_change_response.json()["password"] != RESOURCE_OWNER_PLAIN_PASSWORD

    # ログイン後にパスワードを設定するまで、パスワード変更必須のレスポンスが返ることを確認する
    new_password = password_change_response.json()["password"]
    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": new_password}
    login_response = client.post("/login", json=user_info)
    assert login_response.status_code == 200
    assert login_response.json()["must_change_password"] is True


def test_reset_password_for_not_existing_user(client, get_admin_headers):
    response = client.patch(
        "/admin/users/not_existing_user/password", headers=get_admin_headers)
    assert response.status_code == 404
    assert response.json() == {
        'code': NotFoundCode.USER_NOT_FOUND,
    }


def test_reset_password_by_general_user_denied(client, get_resource_owner_headers):
    response = client.patch(
        "/admin/users/not_existing_user/password", headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        'code': NotAuthorizedCode.NOT_HAVE_PERMISSION,
    }


def test_reset_password_already_must_change_true(client, get_admin_headers, create_resource_owner):
    """ 既にmust_change_passwordがTrueでもエラーにならない """
    first_response = client.patch(
        f"/admin/users/{RESOURCE_OWNER_USERNAME}/password", headers=get_admin_headers)
    assert first_response.status_code == 200
    assert first_response.json()["password"] != RESOURCE_OWNER_PLAIN_PASSWORD

    new_password = first_response.json()["password"]
    """ 既にmust_change_passwordがTrueでもエラーにならない """
    second_response = client.patch(
        f"/admin/users/{RESOURCE_OWNER_USERNAME}/password", headers=get_admin_headers)
    assert second_response.status_code == 200
    assert second_response.json()["password"] != new_password


def test_login_fail_with_old_password_after_change_password(client, get_admin_headers, create_resource_owner):
    password_change_response = client.patch(
        f"/admin/users/{RESOURCE_OWNER_USERNAME}/password", headers=get_admin_headers)
    assert password_change_response.status_code == 200
    assert password_change_response.json()["password"] != RESOURCE_OWNER_PLAIN_PASSWORD

    user_info = {"username": RESOURCE_OWNER_USERNAME,
                 "password": RESOURCE_OWNER_PLAIN_PASSWORD}
    login_response = client.post("/login", json=user_info)
    assert login_response.status_code == 401
    assert login_response.json() == {
        "code": NotAuthorizedCode.LOGIN_FAILED
    }


def test_password_reseted_user_old_token_denied(client, get_admin_headers, get_resource_owner_headers):
    """パスワードがリセットされたユーザーは古いパスワードでログインしたトークンを使用できない"""
    password_reset_response = client.patch(
        f"/admin/users/{RESOURCE_OWNER_USERNAME}/password", headers=get_admin_headers)
    assert password_reset_response.status_code == 200
    data = {"salary": 20.0,
            "year": 2026,
            "month": 10}
    income_response = client.post("/incomes/2026/10", json=data, headers=get_resource_owner_headers)
    assert income_response.status_code == 403
    assert income_response.json() == {
        "code": NotAuthorizedCode.PASSWORD_CHANGE_REQUIRED
    }


def test_reset_password_by_self_denied(client, get_admin_headers):
    """自分のパスワードをリセットしようとした場合はエラーになる"""
    response = client.patch(
        f"/admin/users/{ADMIN_USERNAME}/password", headers=get_admin_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.CANNOT_RESET_OWN_PASSWORD
    }


def test_password_reseted_user_token_before_change_password_denied(client, get_admin_headers, get_resource_owner_headers):
    """
    パスワードがリセットされたユーザーがログインした際に付与される一時アクセス用トークンは
    パスワード再設定後は使用できなくなる"""
    password_reset_response = client.patch(
        f"/admin/users/{RESOURCE_OWNER_USERNAME}/password", headers=get_admin_headers)
    reseted_password = password_reset_response.json()["password"]
    user_info = {
        "username": RESOURCE_OWNER_USERNAME,
        "password": reseted_password
    }
    login_response = client.post("/login", json=user_info)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "new_password": RESOURCE_OWNER_PLAIN_PASSWORD
    }
    password_change_response = client.patch(
        "/password/forced",
        json=data,
        headers=new_headers
    )
    assert password_change_response.status_code == 200
    data = {"salary": 20.0,
            "year": 2026,
            "month": 10}
    income_response = client.post("/incomes/2026/10", json=data, headers=new_headers)
    assert income_response.status_code == 401
    assert income_response.json() == {
        "code": NotAuthorizedCode.NOT_AUTHORIZED
    }
