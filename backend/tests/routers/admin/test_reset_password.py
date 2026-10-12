from testdata import RESOURCE_OWNER_USERNAME, RESOURCE_OWNER_PLAIN_PASSWORD
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
