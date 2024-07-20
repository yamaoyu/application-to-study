from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from security import create_access_token

# 以下の変数は共通で使用し、変更しない
another_test_user = "another testuser"
test_password = "password"


def setup_monthly_income_for_test(client, login_and_get_token):
    data = {"monthly_income": 23, "year_month": "2024-06"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post("/income", json=data, headers=headers)


def setup_create_another_user(client):
    user_info = {"username": another_test_user,
                 "password": test_password}
    client.post("/register", json=user_info)


def setup_login(client):
    user_info = {"username": another_test_user,
                 "password": test_password}
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    return access_token


def test_register_income(client, login_and_get_token):
    data = {"year_month": "2024-06", "monthly_income": 23}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/income", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"message": "2024-06の月収:23.0万円"}


def test_register_income_with_expired_token(client):
    """ 期限の切れたトークンで月収を登録しようとした場合 """
    def mock_create_access_token(data, minutes):
        expires_delta = timedelta(minutes=minutes)
        return create_access_token(data, expires_delta)

    with patch("security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username},
                                                minutes=-30)
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"year_month": "2024-06", "monthly_income": 23}
        response = client.post("/income", json=data, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_register_income_already_registered(client, login_and_get_token):
    """ すでに登録されている月の月収を登録しようとした場合 """
    setup_monthly_income_for_test(client, login_and_get_token)
    data = {"year_month": "2024-06", "monthly_income": 23}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/income", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "その月の月収は既に登録されています。"}


def test_register_income_with_minus_digit(client, login_and_get_token):
    """ 月収をマイナスの値で登録 """
    data = {"year_month": "2024-06", "monthly_income": -23}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/income", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "正の数を入力して下さい"}


def test_get_income(client, login_and_get_token):
    setup_monthly_income_for_test(client, login_and_get_token)
    year_month = "2024-06"
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/income/{year_month}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "今月の詳細": {
            "monthly_income": 23.0,
            "year_month": "2024-06",
            "income_id": 1,
            "username": test_username,
            "bonus": 0.0
        },
        "ボーナス換算後の月収": 23.0
    }


def test_get_income_with_expired_token(client):
    """ 期限の切れたトークンで月収を取得しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        year_month = "2024-06"
        response = client.get(f"/income/{year_month}", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_income_which_another_user_register(client, login_and_get_token):
    """ 他のユーザーが登録した年収はを取得しようとした場合 """
    setup_monthly_income_for_test(client, login_and_get_token)
    setup_create_another_user(client)
    access_token = setup_login(client)
    year_month = "2024-06"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/income/{year_month}", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "その月の月収は未登録です。"}
