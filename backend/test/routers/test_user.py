def setup_register_user_for_test(client):
    user_info = {"usermail": "test@test.com",
                 "password": "testpassword"}
    client.post("/registration", json=user_info)


def test_register_user(client):
    user_info = {"usermail": "test@test.com",
                 "password": "testpassword"}
    response = client.post("/registration", json=user_info)
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{user_info['usermail']}の作成に成功しました。"
    }


def test_register_user_with_invalid_password(client):
    """パスワードの長さが6文字以上、12文字以下でない"""
    user_info = {"usermail": "test@test.com",
                 "password": "test"}
    response = client.post("/registration", json=user_info)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "パスワードは6文字以上、12文字以下としてください"
    }


def test_login(client):
    setup_register_user_for_test(client)
    user_info = {"usermail": "test@test.com",
                 "password": "testpassword"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 200
    assert response.json() == {
        "message": "ログインに成功しました。",
        "usermail": user_info["usermail"]
    }


def test_login_with_invalid_password(client):
    """パスワードを間違えた場合"""
    setup_register_user_for_test(client)
    user_info = {"usermail": "test@test.com",
                 "password": "test"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "パスワードが正しくありません。"
    }


def test_login_not_registered_user(client):
    """登録されていないユーザーでログイン"""
    user_info = {"usermail": "test@test.com",
                 "password": "testpassword"}
    response = client.post("/login", json=user_info)
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"{user_info['usermail']}は登録されていません。"
    }
