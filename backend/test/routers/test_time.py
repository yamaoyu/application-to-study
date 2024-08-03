from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from security import create_access_token

# セットアップ用変数
setup_monthly_income = 23.0
setup_bonus = 0.1
setup_date_path = "/2024/05/05"
setup_date_message = "2024-05-05"


def setup_target_time_for_test(client, get_headers):
    data = {"target_time": 5}
    client.post(f"/activities{setup_date_path}/target",
                json=data,
                headers=get_headers)


def setup_actual_time_for_test(client, get_headers):
    data = {"actual_time": 5}
    client.put(f"/activities{setup_date_path}/actual",
               json=data,
               headers=get_headers)


def setup_finish_activity_for_test(client, get_headers):
    client.put(f"/activities{setup_date_path}/finish",
               headers=get_headers)


def setup_monthly_income_for_test(client, get_headers):
    data = {"monthly_income": setup_monthly_income, "year_month": "2024-05"}
    client.post("/income",
                json=data,
                headers=get_headers)


def test_register_target(client, get_headers):
    data = {"target_time": 5}
    response = client.post(f"/activities{setup_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 201


def test_register_target_with_expired_token(client):
    """ 期限の切れたトークンで目標時間を登録しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        data = {"target_time": 5}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(f"/activities{setup_date_path}/target",
                               json=data,
                               headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_register_target_twice(client, get_headers):
    """ 既に目標時間が登録されている日の目標時間を登録 """
    setup_target_time_for_test(client, get_headers)
    data = {"target_time": 5}
    response = client.post(f"/activities{setup_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": f"{setup_date_message}の目標時間は既に登録済みです"
    }


def test_register_target_missing_zero(client, get_headers):
    """ 日付の書き方が不正(一桁の場合は0xの形式が正しい)の場合 """
    data = {"target_time": 5}
    response = client.post("/activities/2024/5/5/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_actual(client, get_headers):
    setup_target_time_for_test(client, get_headers)
    data = {"actual_time": 5}
    response = client.put(f"/activities{setup_date_path}/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": setup_date_message,
        "target_time": 5,
        "actual_time": data["actual_time"],
        "message": f"活動時間を{data['actual_time']}時間に設定しました。"
    }


def test_register_actual_before_register_target(client, get_headers):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5}
    response = client.put("/activities/2024/05/10/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "先に2024-05-10の目標を入力して下さい"}


def test_register_actual_after_finish(client, get_headers):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    data = {"actual_time": 5}
    response = client.put(f"/activities{setup_date_path}/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail":
                               f"{setup_date_message}の活動実績は既に確定済みです。変更できません"}


def test_finish_activity(client, get_headers):
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    response = client.put(f"/activities{setup_date_path}/finish",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": setup_date_message,
        "target_time": 5.0,
        "actual_time": 5.0,
        "is_achieved": True,
        "message": "目標達成！ボーナス追加！"}


def test_finish_activity_before_register_actual(client, get_headers):
    """ 活動時間登録前に活動を終了しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    response = client.put(f"/activities{setup_date_path}/finish",
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{setup_date_message}の活動時間を登録して下さい"}


def test_finish_activity_without_register_income(client, get_headers):
    """ 月収を登録せずに活動を終了しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    response = client.put(f"/activities{setup_date_path}/finish",
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "2024-05の月収が未登録です"}


def test_get_day_activities(client, get_headers):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    date = setup_date_message
    response = client.get(f"/activities{setup_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "is_achieved": True,
                               "bonus": 0.1}


def test_get_day_activities_before_register_activity(client, get_headers):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-05-10"
    response = client.get("/activities/2024/05/10",
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{date}の情報は登録されていません"}


def test_get_day_activities_with_expired_token(client, get_headers):
    """ 期限の切れたトークンで特定日の状況を取得しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    setup_target_time_for_test(client, get_headers)
    with patch("security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/activities{setup_date_path}",
                              headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_month_acitivities(client, get_headers):
    """ 月ごとの情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    total_monthly_income = setup_monthly_income + setup_bonus
    response = client.get("/activities/2024/05",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"total_monthly_income": total_monthly_income,
                               "base income": setup_monthly_income,
                               "total bonus": setup_bonus,
                               "success days": 1,
                               "activity lists": [{"activity_id": 1,
                                                   "date": "2024-05-05",
                                                   "target": 5.0,
                                                   "actual": 5.0,
                                                   "is_achieved": True,
                                                   "username": test_username}]}
