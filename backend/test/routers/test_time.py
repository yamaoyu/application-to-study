from unittest.mock import patch
from datetime import timedelta
from conftest import test_username
from lib.security import create_access_token

# セットアップ用変数
test_salary = 23.0
test_bonus = test_penalty = 0.58
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
    setup_monthly_income_for_test(client, get_headers)
    data = {"target_time": 5.0}
    response = client.post(f"/activities{test_date_path}/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {"date": test_date,
                               "target_time": 5.0,
                               "actual_time": 0,
                               "status": "pending",
                               "message": f"{test_date}の目標時間を5.0時間に設定しました"}


def test_register_multi_target_without_monthly_income(client, get_headers):
    """ 月収が登録されていない状態で目標時間を登録しようとした場合 """
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": f"{test_date}の目標時間登録に失敗: 2024-5の月収は未登録です"
    }


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
    setup_monthly_income_for_test(client, get_headers)
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


def test_register_multi_target(client, get_headers):
    """ 複数の目標時間を登録した場合 """
    setup_monthly_income_for_test(client, get_headers)
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 201
    assert response.json() == {
        "message": (
            "2024-5-5の目標時間を5.0時間に登録しました\n"
            "2024-5-6の目標時間を6.0時間に登録しました\n"
            "2024-5-7の目標時間を7.0時間に登録しました"
        )
    }


def test_register_multi_target_with_invalid_data(client, get_headers):
    """ 複数の目標時間を登録する際に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_headers)
    # 目標時間が不正
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.2},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 15.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "2024-5-5の目標時間登録に失敗: 目標時間は0.5時間単位で入力してください\n"
            "2024-5-6の目標時間を6.0時間に登録しました\n"
            "2024-5-7の目標時間登録に失敗: 目標時間は0.5~12.0の範囲で入力してください"
        )
    }

    # 日付が不正
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-35", "target_time": 5.0},
            {"date": "2024-13-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        'detail': '2024-5-5の目標時間を5.0時間に登録しました\n'
        '2024-5-35の目標時間登録に失敗: 日付が不正です\n'
        '2024-13-6の目標時間登録に失敗: 月は1~12の範囲で入力してください'
    }


def test_register_actual(client, get_headers):
    setup_monthly_income_for_test(client, get_headers)
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
        "status": "pending",
        "message": f"{test_date}の活動時間を{data['actual_time']}時間に設定しました"
    }


def test_register_actual_before_register_target(client, get_headers):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5.0}
    response = client.put("/activities/2024/5/10/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "2024-5-10の目標時間を先に登録してください"}


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
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    data = {"actual_time": 5.0}
    response = client.put(f"/activities{test_date_path}/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail":
                               f"{test_date}の活動実績は既に確定済みです。変更できません"}


def test_register_multi_actual(client, get_headers):
    """ 複数の活動時間を登録した場合 """
    setup_monthly_income_for_test(client, get_headers)
    # 目標時間を複数登録
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_headers)
    # 活動時間を登録
    data = {
        "activities": [
            {"date": "2024-5-5", "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 6.0},
            {"date": "2024-5-7", "actual_time": 7.0}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": (
            "2024-5-5の活動時間を5.0時間に登録しました\n"
            "2024-5-6の活動時間を6.0時間に登録しました\n"
            "2024-5-7の活動時間を7.0時間に登録しました"
        )
    }


def test_register_multi_actual_with_invalid_data(client, get_headers):
    """ 複数の活動時間を登録する際に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_headers)
    # 目標時間を複数登録
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_headers)
    # 活動時間を登録
    data = {
        "activities": [
            {"date": "2024-5-5", "actual_time": 5.2},  # 不正な活動時間
            {"date": "2024-5-6", "actual_time": 6.0},
            {"date": "2024-5-7", "actual_time": 15.0}  # 上限を超える活動時間
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "2024-5-5の活動時間登録に失敗: 活動時間は0.5時間単位で入力してください\n"
            "2024-5-6の活動時間を6.0時間に登録しました\n"
            "2024-5-7の活動時間登録に失敗: 活動時間は0.0~12.0の範囲で入力してください"
        )
    }

    data = {
        "activities": [
            {"date": "20240-5-5", "actual_time": 5.0},
            {"date": "2024-15-6", "actual_time": 6.0},
            {"date": "2024-5-7", "actual_time": 7.0}
        ]
    }

    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "20240-5-5の活動時間登録に失敗: 年は2024~2099の範囲で入力してください\n"
            "2024-15-6の活動時間登録に失敗: 月は1~12の範囲で入力してください\n"
            "2024-5-7の活動時間を7.0時間に登録しました"
        )
    }


def test_update_already_finished_activity(client, get_headers):
    """ 既に終了した活動の時間を更新しようとした場合 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    # 目標時間を登録する活動の中に既に終了した活動が含まれている場合
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "2024-5-5の目標時間登録に失敗: 目標時間は既に登録済みです\n"
            "2024-5-6の目標時間を6.0時間に登録しました"
        )
    }

    # 活動時間を登録する活動の中に既に終了した活動が含まれている場合
    data = {
        "activities": [
            {"date": "2024-5-5", "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 6.0}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "2024-5-5の活動時間登録に失敗: 既に確定されています\n"
            "2024-5-6の活動時間を6.0時間に登録しました"
        )
    }


def test_finish_activity(client, get_headers):
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    response = client.put(f"/activities{test_date_path}/finish",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": test_date,
        "target_time": 5.0,
        "actual_time": 5.0,
        "status": "success",
        "message": f"目標達成！{f"{test_bonus}万円({int(test_bonus * 10000)}円)"}ボーナス追加！"}


def test_finish_multi_activity(client, get_headers):
    """ 複数の活動を終了させた場合 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    # 今回のテストでのボーナス等を定義
    pay_adjustment = 1.04
    total_bonus = 1.39
    total_penalty = 0.35
    # 複数の目標時間を登録
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_headers)
    # 複数の活動時間を登録
    data = {
        "activities": [
            {"date": "2024-5-5", "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 3.0},
            {"date": "2024-5-7", "actual_time": 7.0}
        ]
    }
    client.put("/activities/multi/actual",
               json=data,
               headers=get_headers)
    # 活動を終了
    data = {
        "dates": ["2024-5-5", "2024-5-6", "2024-5-7"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": (
            "2024-5-5の活動を終了:ボーナス0.58万円(5800円)\n"
            "2024-5-6の活動を終了:ペナルティ0.35万円(3500円)\n"
            "2024-5-7の活動を終了:ボーナス0.81万円(8100円)"
        ),
        "pay_adjustment": f"{pay_adjustment}万円({int(pay_adjustment * 10000)}円)",
        "total_bonus": f"{total_bonus}万円({int(total_bonus * 10000)}円)",
        "total_penalty": f"{total_penalty}万円({int(total_penalty * 10000)}円)"
    }


def test_finish_multi_activity_with_invalid_data(client, get_headers):
    """ 複数の活動を終了させた場合に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_headers)
    # 複数の目標時間を登録
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_headers)
    # 複数の活動時間を登録
    data = {
        "activities": [
            {"date": "2024-5-5", "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 6.0}
        ]
    }
    client.put("/activities/multi/actual",
               json=data,
               headers=get_headers)
    # 活動を終了
    # 既に終了した日のテストのために2024-5-6のみ終了にする
    client.put("/activities/multi/finish",
               json={"dates": ["2024-5-6"]}, headers=get_headers)
    data = {
        "dates": ["2024-5-5", "2024-5-6", "2024-5-8", "20241-5-5", "2024-15-6", "2024-5-71"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_headers)
    assert response.status_code == 400
    # 登録に成功した日/既に終了した日/目標時間の登録がない日/不正な年/不正な月/不正な日付
    assert response.json() == {
        "detail": (
            "2024-5-5の活動を終了:ボーナス0.58万円(5800円)\n"
            "2024-5-6の活動終了に失敗: 2024-5-6の実績は確定済みです\n"
            "2024-5-8の活動終了に失敗: 2024-5-8の活動記録は未登録です\n"
            "20241-5-5の活動終了に失敗: 年は2024~2099の範囲で入力してください\n"
            "2024-15-6の活動終了に失敗: 月は1~12の範囲で入力してください\n"
            "2024-5-71の活動終了に失敗: 日付が不正です"
        )
    }


def test_finish_multi_acitivity_with_no_dates(client, get_headers):
    """ 複数の活動を終了させた場合に日付が指定されていない場合 """
    response = client.put("/activities/multi/finish",
                          json={},
                          headers=get_headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "日付を指定してください"}


def test_get_day_activities_registered_target(client, get_headers):
    """ 目標時間登録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    date = test_date
    response = client.get(f"/activities{test_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 0,
                               "status": "pending",
                               "bonus": 0,
                               "penalty": test_penalty}


def test_get_day_activities_registered_actual(client, get_headers):
    """ 活動時間登録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    date = test_date
    response = client.get(f"/activities{test_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "status": "pending",
                               "bonus": test_bonus,
                               "penalty": 0}


def test_get_day_activities(client, get_headers):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    date = test_date
    response = client.get(f"/activities{test_date_path}",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "status": "success",
                               "bonus": test_bonus,
                               "penalty": 0}


def test_get_day_activities_before_register_activity(client, get_headers):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-5-10"
    response = client.get("/activities/2024/5/10",
                          headers=get_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"{date}の活動記録は未登録です"}


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
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/2024/5",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_monthly_income,
                               "salary": test_salary,
                               "pay_adjustment": test_bonus,
                               "bonus": test_bonus,
                               "penalty": 0,
                               "success_days": 1,
                               "fail_days": 0,
                               "activity_list": [{"activity_id": 1,
                                                  "date": "2024-05-05",
                                                  "target_time": 5.0,
                                                  "actual_time": 5.0,
                                                  "status": "success",
                                                  "bonus": test_bonus,
                                                  "penalty": 0,
                                                  "username": test_username}]}


def test_get_all_acitivities(client, get_headers):
    """ 対象ユーザーのすべての情報を取得 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/total",
                          headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_monthly_income,
                               "salary": test_salary,
                               "pay_adjustment": test_bonus,
                               "bonus": test_bonus,
                               "penalty": 0,
                               "success_days": 1,
                               "fail_days": 0}


def test_get_year_acitivities(client, get_headers):
    """ 月ごとの情報を取得 """
    setup_monthly_income_for_test(client, get_headers)
    setup_target_time_for_test(client, get_headers)
    setup_actual_time_for_test(client, get_headers)
    setup_finish_activity_for_test(client, get_headers)
    total_income = test_salary + test_bonus
    response = client.get("/activities/2024", headers=get_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_income,
                               "salary": test_salary,
                               "pay_adjustment": test_bonus,
                               "bonus": test_bonus,
                               "penalty": 0,
                               "success_days": 1,
                               "fail_days": 0,
                               "monthly_info": {
                                   "jan": {},
                                   "feb": {},
                                   "mar": {},
                                   "apr": {},
                                   "may": {
                                       "salary": test_salary,
                                       "bonus": test_bonus,
                                       "penalty": 0.0,
                                       "pay_adjustment": test_bonus,
                                       "success_days": 1,
                                       "fail_days": 0},
                                   "jun": {},
                                   "jul": {},
                                   "aug": {},
                                   "sep": {},
                                   "oct": {},
                                   "nov": {},
                                   "dec": {}
                               }}


def test_get_acitivities_with_wrong_status(client, get_headers):
    """ ステータス名を間違えた状態で取得 """
    response = client.get("/activities?status=pendin", headers=get_headers)
    assert response.status_code == 422
