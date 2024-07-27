from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from security import create_access_token


def setup_target_time_for_test(client, get_headers):
    data = {"date": "2024-05-05", "target_time": 5}
    client.post("/target", json=data, headers=get_headers)


def setup_actual_time_for_test(client, get_headers):
    data = {"actual_time": 5, "date": "2024-05-05"}
    client.put("/actual", json=data, headers=get_headers)


def setup_finish_activity_for_test(client, get_headers):
    data = {"date": "2024-05-05"}
    client.put("/finish", json=data, headers=get_headers)


def setup_monthly_income_for_test(client, get_headers):
    data = {"monthly_income": 23, "year_month": "2024-05"}
    client.post("/income", json=data, headers=get_headers)


def test_register_target(client, get_headers):
    data = {"date": "2024-05-05", "target_time": 5}
    response = client.post("/target", json=data, headers=get_headers)
    assert response.status_code == 201


def test_register_target_with_expired_token(client):
    """ 期限の切れたトークンで目標時間を登録しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        data = {"date": "2024-05-05", "target_time": 5}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/target", json=data, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_register_target_without_slash(client, get_headers):
    """ 日付の形式が-ではなく/の場合 """
    data = {"date": "2024/05/05", "target_time": 5}
    response = client.post("/target", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_target_missing_zero(client, get_headers):
    """ 日付の書き方が不正(一桁の場合は0xの形式が正しい)の場合 """
    data = {"date": "2024-5-5", "target_time": 5}
    response = client.post("/target", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_actual(client, get_headers):
    setup_target_time_for_test(client, get_headers)
    data = {"actual_time": 5, "date": "2024-05-05"}
    response = client.put("/actual", json=data, headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": data['date'],
        "target_time": 5,
        "actual_time": data["actual_time"],
        "message": f"活動時間を{data['actual_time']}時間に設定しました。"
    }


def test_register_actual_before_register_target(client, get_headers):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5, "date": "2024-05-06"}
    response = client.put("/actual", json=data, headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"先に{data['date']}の目標を入力して下さい"}


def test_register_actual_after_finish(client, get_headers):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    data = {"actual_time": 5, "date": "2024-05-05"}
    response = client.put("/actual", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail":
                               f"{data['date']}の活動実績は既に確定済みです。変更できません"}


def test_finish_activity(client, get_headers):
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data, headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": data["date"],
        "target_time": 5.0,
        "actual_time": 5.0,
        "is_achieved": True,
        "message": "目標達成！ボーナス追加！"}


def test_finish_activity_before_register_actual(client, get_headers):
    """ 活動時間登録前に活動を終了しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{data['date']}の活動時間を登録して下さい"}


def test_finish_activity_without_register_income(client, get_headers):
    """ 月収を登録せずに活動を終了しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data, headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "2024-05の月収が未登録です"}


def test_get_today_situation(client, get_headers):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    date = "2024-05-05"
    response = client.get(f"/situation/{date}", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "is_achieved": True,
                               "bonus": 0.1,
                               "username": test_username}


def test_get_today_situation_before_register_activity(client, get_headers):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-05-10"
    response = client.get(f"/situation/{date}", headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{date}の情報は登録されていません"}


def test_get_situation_with_expired_token(client, get_headers):
    """ 期限の切れたトークンである日の状況を取得しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    setup_target_time_for_test(client, get_headers)
    with patch("security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        date = "2024-05-05"
        response = client.get(f"/situation/{date}", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}
