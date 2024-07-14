import pytest
from conftest import test_username, test_plain_password, SECRET_KEY
from jose import jwt


def test_register_user(client):
    user_info = {"username": "test",
                 "password": "testpassword"}
    response = client.post("/register", json=user_info)
    assert response.status_code == 200
    assert response.json() == {
        "username": "test",
        "password": "************",
        "email": None,
        "message": "testの作成に成功しました。"
    }


def test_register_user_with_invalid_password(client):
    """6文字以上、12文字以下でないパスワードで登録した場合"""
    user_info = {"username": "test",
                 "password": "test"}
    response = client.post("/register", json=user_info)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "パスワードは6文字以上、12文字以下としてください"
    }


def test_login(client):
    user_info = {"username": test_username,
                 "password": test_plain_password}
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    # HS256により作成されるアクセストークンは最低100文字
    assert len(access_token) >= 100
    try:
        decoded_token = jwt.decode(
            access_token, SECRET_KEY, algorithms=['HS256'])
        assert "sub" in decoded_token
        assert decoded_token["sub"] == "testuser"
        # 必要に応じて他のクレームもチェック
    except jwt.JWTError as e:
        pytest.fail(f"Invalid JWT token{e}")


def test_login_with_invalid_password(client):
    """パスワードを間違えた場合"""
    user_info = {"username": test_username,
                 "password": "invalid_password"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "パスワードが正しくありません。"
    }


def test_login_not_registered_user(client):
    """登録されていないユーザーでログイン"""
    user_info = {"username": "test",
                 "password": "testpassword"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 404
