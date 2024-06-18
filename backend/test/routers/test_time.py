import pytest


@pytest.fixture
def register_target(client):
    data = {"date": "2024-05-05", "target_hour": 5}
    client.post("/target", json=data)


@pytest.fixture
def register_actual(client, register_target):
    data = {"actual_time": 5, "date": "2024-05-05"}
    client.put("/actual", json=data)


@pytest.fixture
def finish_activity(client, register_actual):
    data = {"date": "2024-05-05"}
    client.put("/finish", json=data)


@pytest.fixture
def register_monthly_income(client):
    data = {"monthly_income": 23, "year_month": "2024-05"}
    client.post("/income", json=data)


def test_register_target(client):
    data = {"date": "2024-05-05", "target_hour": 5}
    response = client.post("/target", json=data)
    assert response.status_code == 201


def test_register_target_incorrect_date_format_slash(client):
    """ 日付の形式が-ではなく/の場合 """
    data = {"date": "2024/05/05", "target_hour": 5}
    response = client.post("/target", json=data)
    assert response.status_code == 400


def test_register_target_incorrect_date_format_missing_zero(client):
    """ 日付の書き方が不正(一桁の場合は0xの形式が正しい)の場合 """
    data = {"date": "2024-5-5", "target_hour": 5}
    response = client.post("/target", json=data)
    assert response.status_code == 400


def test_register_actual(client):
    data = {"actual_time": 5, "date": "2024-05-05"}
    response = client.put("/actual", json=data)
    assert response.status_code == 200


def test_register_actual_before_register_target(client):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5, "date": "2024-05-06"}
    response = client.put("/actual", json=data)
    assert response.status_code == 400


def test_register_actual_after_finish(client, finish_activity):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    data = {"actual_time": 5, "date": "2024-05-06"}
    response = client.put("/actual", json=data)
    assert response.status_code == 400


def test_finish_activity(client, register_actual, register_monthly_income):
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data)
    assert response.status_code == 200


def test_finish_activity_before_register_actual(client, register_target):
    """ 活動時間登録前に活動を終了しようとした場合 """
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data)
    assert response.status_code == 400


def test_finish_activity_without_register_income(client, register_actual):
    """ 月収を登録せずに活動を終了しようとした場合 """
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data)
    assert response.status_code == 400
