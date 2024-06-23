# 事前処理

def setup_monthly_income_for_test(client):
    data = {"monthly_income": 23, "year_month": "2024-06"}
    client.post("/income", json=data)

# 事前処理ここまで


# 以降テスト関数

def test_register_income(client):
    data = {"year_month": "2024-06", "monthly_income": 23}
    response = client.post("/income", json=data)
    assert response.status_code == 201
    assert response.json() == {"message": "2024-06の月収:23.0万円"}


def test_register_income_already_registered(client):
    """ すでに登録されている月の月収を登録しようとした場合 """
    setup_monthly_income_for_test(client)
    data = {"year_month": "2024-06", "monthly_income": 23}
    response = client.post("/income", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "その月の月収は既に登録されています。"}


def test_register_income_with_minus_digit(client):
    """ 月収をマイナスの値で登録 """
    data = {"year_month": "2024-06", "monthly_income": -23}
    response = client.post("/income", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "正の数を入力して下さい"}


def test_get_income(client):
    setup_monthly_income_for_test(client)
    year_month = "2024-06"
    response = client.get(f"/income/{year_month}")
    assert response.status_code == 200
    assert response.json() == {
        "今月の詳細": {
            "monthly_income": 23.0,
            "year_month": "2024-06",
            "income_id": 1,
            "bonus": 0.0
        },
        "ボーナス換算後の月収": 23.0
    }
