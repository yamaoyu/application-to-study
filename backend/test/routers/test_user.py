import pytest
from conftest import test_username, test_plain_password, SECRET_KEY, ALGORITHM, password_for_another_user
from jose import jwt


def test_register_user(client):
    user_info = {"username": "test",
                 "password": password_for_another_user}
    response = client.post("/users", json=user_info)
    assert response.status_code == 201
    assert response.json() == {
        "username": "test",
        "password": "*********",
        "email": None,
        "message": "testの作成に成功しました",
        "role": "general"
    }


def test_register_user_with_short_username(client):
    """3文字以上、16文字以下でないユーザー名で登録した場合"""
    user_info = {"username": "t",
                 "password": password_for_another_user}
    response = client.post("/users", json=user_info)
    assert response.status_code == 422
    assert response.json() == {"detail": "ユーザー名は3文字以上、16文字以下としてください"}


def test_register_user_with_invalid_password(client):
    """8文字以上、16文字以下でないパスワードで登録した場合"""
    user_info = {"username": "test",
                 "password": "test"}
    response = client.post("/users", json=user_info)
    assert response.status_code == 422
    assert response.json() == {"detail": "パスワードは8文字以上、16文字以下としてください"}


def test_register_user_with_invalid_email(client):
    """「@」が含まれないメールアドレスを登録した場合"""
    user_info = {"username": "test",
                 "password": password_for_another_user,
                 "email": "aaaaa"}
    response = client.post("/users", json=user_info)
    assert response.status_code == 422
    assert response.json() == {"detail": "正しい形式のメールアドレスを入力してください"}


def test_register_with_duplicate_user_name(client):
    """ 既に登録されているユーザー名で登録した場合 """
    user_info = {"username": test_username,
                 "password": password_for_another_user}
    response = client.post("/users", json=user_info)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "入力された情報は既に使用されています。\n別のユーザー名またはメールアドレスをお試しください"
    }


def test_login(client):
    user_info = {"username": test_username,
                 "password": test_plain_password}
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
    # 作成されるトークンは最低100文字
    assert len(access_token) >= 100
    assert len(refresh_token) >= 100
    try:
        for token in [access_token, refresh_token]:
            decoded_token = jwt.decode(
                token, SECRET_KEY, ALGORITHM)
            assert "sub" in decoded_token
            assert decoded_token["sub"] == "testuser"
    except jwt.JWTError as e:
        pytest.fail(f"Invalid JWT token {str(e)}")


def test_login_with_invalid_password(client):
    """パスワードを間違えた場合"""
    user_info = {"username": test_username,
                 "password": "invalid_password"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 401
    assert response.json() == {
        "detail": "入力情報が正しくありません。\nユーザー名またはパスワードをご確認ください"
    }


def test_login_not_registered_user(client):
    """登録されていないユーザーでログイン"""
    user_info = {"username": "test",
                 "password": password_for_another_user}
    response = client.post("/login", json=user_info)
    assert response.status_code == 404


def test_logout(client, get_headers):
    response = client.post("/logout", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"{test_username}がログアウト"}


def test_regenerate_token(client, get_headers):
    response = client.post("/token", headers=get_headers)
    access_token = response.json()["access_token"]
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"
    assert len(access_token) >= 100
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
        assert "sub" in decoded_token
        assert decoded_token["sub"] == "testuser"
    except jwt.JWTError as e:
        pytest.fail(f"Invalid JWT token {str(e)}")
