from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from lib.security import create_access_token

# セットアップ用変数
test_salary = 23.0
test_bonus = 0.1
test_date_path = "/2024/5/5"
test_date = "2024-5-5"
test_year = "2024"
test_month = "5"


def setup_target_time_for_test(client, get_headers):
    data = {"target_time": 5.0}
    client.post(f"/activities{test_date_path}/target",
                json=data,
                headers=get_headers)


def setup_actual_time_for_test(client, get_headers):
    data = {"actual_time": 5.0}
    client.put(f"/activities{test_date_path}/actual",
               json=data,
               headers=get_headers)


def setup_finish_activity_for_test(client, get_headers):
    client.put(f"/activities{test_date_path}/finish",
               headers=get_headers)


def setup_monthly_income_for_test(client, get_headers):
    data = {"salary": test_salary,
            "year": test_year,
            "month": test_month}
    client.post(f"/incomes/{test_year}/{test_month}",
                json=data,
                headers=get_headers)


def test_register_target(client, get_headers):
    data = {"target_time": 5.0}
    response = client.post(f"/activities{test_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {"date": test_date,
                               "target_time": 5.0,
                               "actual_time": 0,
                               "is_achieved": False,
                               "message": f"{test_date}の目標時間を5.0時間に設定しました"}


def test_register_target_with_expired_token(client):
    """ 期限の切れたトークンで目標時間を登録しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("lib.security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": test_username})
        data = {"target_time": 5}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(f"/activities{test_date_path}/target",
                               json=data,
                               headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_register_target_twice(client, get_headers):
    """ 既に目標時間が登録されている日の目標時間を登録 """
    setup_target_time_for_test(client, get_headers)
    data = {"target_time": 5.0}
    response = client.post(f"/activities{test_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": f"{test_date}の目標時間は既に登録済みです"
    }


def test_register_target_out_of_range(client, get_headers):
    """ 入力上限の12時間を超えた目標時間を登録 """
    data = {"target_time": 12.5}
    response = client.post(f"/activities{test_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "目標時間は0.5~12.0の範囲で入力してください"}


def test_register_target_with_incorrect_hour(client, get_headers):
    """ 0.5単位でない時間を入力した場合 """
    data = {"target_time": 2.3}
    response = client.post(f"/activities{test_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "目標時間は0.5時間単位で入力してください"}


def test_register_target_with_invalid_year(client, get_headers):
    """ 年が2024 <= year <= 2099ではない """
    data = {"target_time": 5.0}
    response = client.post("/activities/2022/6/30/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "年は2024~2099の範囲で入力してください"}


def test_register_target_with_invalid_date(client, get_headers):
    """ 存在しない日付の場合 """
    data = {"target_time": 5.0}
    response = client.post("/activities/2024/6/31/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "日付が不正です"}


def test_register_actual(client, get_headers):
    setup_target_time_for_test(client, get_headers)
    data = {"actual_time": 5.0}
    response = client.put(f"/activities{test_date_path}/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": test_date,
        "target_time": 5.0,
        "actual_time": data["actual_time"],
        "is_achieved": False,
        "message": f"活動時間を{data['actual_time']}時間に設定しました"
    }


def test_register_actual_before_register_target(client, get_headers):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5.0}
    response = client.put("/activities/2024/5/10/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "先に2024-5-10の目標を入力して下さい"}


def test_register_actual_with_invalid_hour(client, get_headers):
    """ 時間を1x.0or5、もしくはx.0or5の形で入力していない場合 """
    setup_target_time_for_test(client, get_headers)
    data = {"actual_time": 5.2}
    response = client.put("/activities/2024/5/5/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "活動時間は0.5時間単位で入力してください"}


def test_register_actual_after_finish(client, get_headers):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    data = {"actual_time": 5.0}
    response = client.put(f"/activities{test_date_path}/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail":
                               f"{test_date}の活動実績は既に確定済みです。変更できません"}


def test_finish_activity(client, get_headers):
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    response = client.put(f"/activities{test_date_path}/finish",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": test_date,
        "target_time": 5.0,
        "actual_time": 5.0,
        "is_achieved": True,
        "message": "目標達成！ボーナス追加！"}


def test_finish_activity_without_register_income(client, get_headers):
    """ 月収を登録せずに活動を終了しようとした場合 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    response = client.put(f"/activities{test_date_path}/finish",
                          headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail":
                               f"{test_year}-{test_month}の月収が未登録です"}


def test_get_day_activities_registered_target(client, get_headers):
    """ 目標時間登録まで行った日の情報を取得 """
    setup_target_time_for_test(client, get_headers)
    date = test_date
    response = client.get(f"/activities{test_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 0,
                               "is_achieved": False,
                               "bonus": 0}


def test_get_day_activities_registered_actual(client, get_headers):
    """ 活動時間登録まで行った日の情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    date = test_date
    response = client.get(f"/activities{test_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "is_achieved": False,
                               "bonus": 0}


def test_get_day_activities(client, get_headers):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    date = test_date
    response = client.get(f"/activities{test_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "is_achieved": True,
                               "bonus": 0.1}


def test_get_day_activities_before_register_activity(client, get_headers):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-5-10"
    response = client.get("/activities/2024/5/10",
                          headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"{date}の情報は未登録です"}


def test_get_day_activities_with_expired_token(client, get_headers):
    """ 期限の切れたトークンで特定日の状況を取得しようとした場合 """
    def mock_create_expired_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    setup_target_time_for_test(client, get_headers)
    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": test_username})
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/activities{test_date_path}",
                              headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_month_acitivities(client, get_headers):
    """ 月ごとの情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/2024/5",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"total_monthly_income": total_monthly_income,
                               "salary": test_salary,
                               "total_bonus": test_bonus,
                               "success_days": 1,
                               "fail_days": 0,
                               "activity_list": [{"activity_id": 1,
                                                  "date": "2024-05-05",
                                                  "target_time": 5.0,
                                                  "actual_time": 5.0,
                                                  "is_achieved": True,
                                                  "username": test_username}]}


def test_get_all_acitivities(client, get_headers):
    """ 対象ユーザーのすべての情報を取得 """
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_monthly_income_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/total",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_monthly_income,
                               "total_salary": test_salary,
                               "total_bonus": test_bonus,
                               "success_days": 1,
                               "fail_days": 0}
