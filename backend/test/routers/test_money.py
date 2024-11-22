from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from lib.security import create_access_token

# テストで使用する変数
another_test_user = "testuser2"
test_password = "password"
test_year = "2024"
test_month = "6"
test_salary = 23.0


def setup_salary_for_test(client, get_headers):
    data = {"salary": test_salary,
            "year": test_year,
            "month": test_month}
    client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=get_headers)


def setup_create_another_user(client):
    user_info = {"username": another_test_user,
                 "password": test_password, }
    client.post("/users", json=user_info)


def setup_login(client):
    user_info = {"username": another_test_user,
                 "password": test_password,
                 "email": "another_test@test.com"}
    response = client.post("/login", json=user_info)
    access_token = response.json()["access_token"]
    return access_token


def test_register_income(client, get_headers):
    data = {"salary": test_salary,
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {
        "message": f"{test_year}-{test_month}の月収:{test_salary}万円"}


def test_register_income_with_string(client, get_headers):
    data = {"salary": "aaaaa",
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"error": "数値を入力してください"}


def test_register_income_with_expired_token(client):
    """ 期限の切れたトークンで月収を登録しようとした場合 """
    def mock_create_expired_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"salary": test_salary,
                "year": test_year,
                "month": test_month}
        response = client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_register_income_already_registered(client, get_headers):
    """ すでに登録されている月の月収を登録しようとした場合 """
    setup_salary_for_test(client, get_headers)
    data = {"salary": test_salary,
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "その月の月収は既に登録されています"}


def test_register_income_with_minus_digit(client, get_headers):
    """ 月収をマイナスの値で登録 """
    data = {"salary": -23.0,
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"error": "給料は正の数を入力して下さい"}


def test_get_income(client, get_headers):
    setup_salary_for_test(client, get_headers)
    year = test_year
    month = test_month
    response = client.get(f"/incomes/{year}/{month}", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "今月の詳細": {
            "salary": test_salary,
            "year_month": f"{test_year}-{test_month}",
            "income_id": 1,
            "username": test_username,
            "bonus": 0.0
        },
        "ボーナス換算後の月収": test_salary
    }


def test_get_income_with_expired_token(client):
    """ 期限の切れたトークンで月収を取得しようとした場合 """
    def mock_create_expired_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        year = test_year
        month = test_month
        response = client.get(f"/incomes/{year}/{month}", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_income_by_another_user(client, get_headers):
    """ 他のユーザーが登録した年収はを取得しようとした場合 """
    setup_salary_for_test(client, get_headers)
    setup_create_another_user(client)
    access_token = setup_login(client)
    year = test_year
    month = test_month
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/incomes/{year}/{month}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"{year}-{month}の月収は未登録です"}
