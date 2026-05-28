from unittest.mock import patch
from datetime import timedelta
from testdata import RESOURCE_OWNER_USERNAME
from lib.security import create_access_token
from app.domain.activity_calculator import round_money

# セットアップ用変数
test_salary = 23.0
test_bonus = test_penalty = 0.58
test_date_path = "/2024/5/5"
test_date = "2024-5-5"
test_year = "2024"
test_month = "5"


def setup_target_time_for_test(client, get_resource_owner_headers, target_date=test_date):
    data = {
        "activities": [
            {"date": target_date, "target_time": 5.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_resource_owner_headers)


def setup_actual_time_for_test(client, get_resource_owner_headers):
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    client.put("/activities/multi/actual",
               json=data,
               headers=get_resource_owner_headers)


def setup_finish_activity_for_test(client, get_resource_owner_headers):
    data = {
        "dates": [test_date]
    }
    client.put("/activities/multi/finish",
               json=data,
               headers=get_resource_owner_headers)


def setup_monthly_income_for_test(client, get_resource_owner_headers):
    data = {"salary": test_salary}
    client.post(f"/incomes/{test_year}/{test_month}",
                json=data,
                headers=get_resource_owner_headers)


def test_register_multi_target_without_monthly_income(client, get_resource_owner_headers):
    """ 月収が登録されていない状態で目標時間を登録しようとした場合 """
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": "income_not_found"
            }
        ]
    }


def test_register_target_with_expired_token(client, get_resource_owner_headers):
    """ 期限の切れたトークンで目標時間を登録しようとした場合 """
    def mock_create_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    with patch("lib.security.create_access_token", mock_create_access_token):
        access_token = mock_create_access_token(data={"sub": RESOURCE_OWNER_USERNAME})
        headers = {"Authorization": f"Bearer {access_token}"}
        setup_monthly_income_for_test(client, get_resource_owner_headers)
        data = {
            "activities": [
                {"date": test_date, "target_time": 5.0}
            ]
        }
        response = client.post("/activities/multi/target",
                               json=data,
                               headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_register_target_twice(client, get_resource_owner_headers):
    """ 既に目標時間が登録されている日の目標時間を登録 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": "target_time_already_registered"
            }
        ]
    }


def test_register_target_out_of_range(client, get_resource_owner_headers):
    """ 入力上限の12時間を超えた目標時間を登録 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 15.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "目標時間は0.5~12.0の範囲で入力してください"}


def test_register_target_with_incorrect_hour(client, get_resource_owner_headers):
    """ 0.5単位でない時間を入力した場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.3}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "目標時間は0.5時間単位で入力してください"}


def test_register_target_with_invalid_year(client, get_resource_owner_headers):
    """ 年が2024 <= year <= 2099ではない """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "20240-5-5", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "年は2024~2099の範囲で入力してください"}


def test_register_target_with_invalid_month(client, get_resource_owner_headers):
    """ 存在しない月の場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-13-30", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "月は1~12の範囲で入力してください"}


def test_register_target_with_invalid_date(client, get_resource_owner_headers):
    """ 存在しない月の場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-2-30", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "日付が不正です"}


def test_register_multi_target(client, get_resource_owner_headers):
    """ 複数の目標時間を登録した場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "success",
                "target_time": 5.0
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "target_time": 6.0
            },
            {
                "date": "2024-5-7",
                "result": "success",
                "target_time": 7.0
            }
        ]
    }


def test_register_multi_target_already_registered(client, get_resource_owner_headers):
    """ 既に目標時間が登録された日が含まれる場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": "2024-5-5",
                "result": "error",
                "reason": "target_time_already_registered"
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "target_time": 6.0
            }
        ]
    }


def test_register_multi_target_with_invalid_data(client, get_resource_owner_headers):
    """ 複数の目標時間を登録する際に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    # 目標時間が不正
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.2},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 15.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "目標時間は0.5時間単位で入力してください"
    }

    # 年が不正
    data = {
        "activities": [
            {"date": "20240-5-5", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        'detail': "年は2024~2099の範囲で入力してください"
    }

    data = {
        "activities": [
            {"date": "2024-13-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "月は1~12の範囲で入力してください"
    }

    # 日付が不正
    data = {
        "activities": [
            {"date": "2024-5-35", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        'detail': '日付が不正です'
    }


def test_register_multi_actual(client, get_resource_owner_headers):
    """ 複数の活動時間を登録した場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    # 目標時間を複数登録
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_resource_owner_headers)
    # 活動時間を登録
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 6.0},
            {"date": "2024-5-7", "actual_time": 7.0}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "success",
                "actual_time": 5.0
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "actual_time": 6.0
            },
            {
                "date": "2024-5-7",
                "result": "success",
                "actual_time": 7.0
            }
        ]
    }


def test_register_actual_before_register_target(client, get_resource_owner_headers):
    """ 目標時間登録前に活動時間を登録した場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-10", "actual_time": 5.0},
            {"date": "2024-5-11", "actual_time": 5.0}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "date": "2024-5-10",
                "result": "error",
                "reason": "activity_not_found"
            },
            {
                "date": "2024-5-11",
                "result": "error",
                "reason": "activity_not_found"
            }
        ]
    }


def test_register_actual_with_invalid_hour(client, get_resource_owner_headers):
    """ 時間を1x.0or5、もしくはx.0or5の形で入力していない場合 """
    setup_target_time_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-10", "actual_time": 5.2}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "活動時間は0.5時間単位で入力してください"}


def test_register_actual_after_finish(client, get_resource_owner_headers):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": "activity_already_finished"
            }
        ]
    }


def test_register_multi_actual_with_invalid_data(client, get_resource_owner_headers):
    """ 複数の活動時間を登録する際に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    # 活動時間を登録
    data = {
        "activities": [
            {"date": test_date, "actual_time": 15.0}  # 上限を超える活動時間
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "活動時間は0.0~12.0の範囲で入力してください"
        )
    }

    data = {
        "activities": [
            {"date": "20240-5-5", "actual_time": 5.0}
        ]
    }

    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "年は2024~2099の範囲で入力してください"
    }


def test_update_already_finished_activity(client, get_resource_owner_headers):
    """ 既に終了した活動と同じ日に目標時間や活動時間を登録しようとした場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    # 目標時間を登録する活動の中に既に終了した活動が含まれている場合
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0}
        ]
    }
    response = client.post("/activities/multi/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": "target_time_already_registered"
            }
        ]
    }

    # 活動時間を登録する活動の中に既に終了した活動が含まれている場合
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    response = client.put("/activities/multi/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": "activity_already_finished"
            }
        ]
    }


def test_finish_multi_activity(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    # 今回のテストでのボーナス等を定義
    total_bonus = 1.39
    total_penalty = 0.35
    pay_adjustment = round_money(total_bonus - total_penalty)
    # 複数の目標時間を登録
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_resource_owner_headers)
    # 複数の活動時間を登録
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 3.0},
            {"date": "2024-5-7", "actual_time": 7.0}
        ]
    }
    client.put("/activities/multi/actual",
               json=data,
               headers=get_resource_owner_headers)
    # 活動を終了
    data = {
        "dates": [test_date, "2024-5-6", "2024-5-7"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "pay_adjustment": pay_adjustment,
        "total_bonus": total_bonus,
        "total_penalty": total_penalty,
        "results": [
            {"date": "2024-5-5", "result": "success", "status": "success", "bonus": 0.58, "penalty": 0.0},
            {"date": "2024-5-6", "result": "success", "status": "failure", "bonus": 0.0, "penalty": 0.35},
            {"date": "2024-5-7", "result": "success", "status": "success", "bonus": 0.81, "penalty": 0.0}
        ]
    }


def test_finish_multi_activity_with_errors(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    # 今回のテストでのボーナス等を定義
    total_bonus = 0.81
    total_penalty = 0.35
    pay_adjustment = round_money(total_bonus - total_penalty)
    # 複数の目標時間を登録
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/multi/target",
                json=data,
                headers=get_resource_owner_headers)
    # 複数の活動時間を登録
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
            {"date": "2024-5-6", "actual_time": 3.0},
            {"date": "2024-5-7", "actual_time": 7.0}
        ]
    }
    client.put("/activities/multi/actual",
               json=data,
               headers=get_resource_owner_headers)
    # 活動を終了
    data = {
        "dates": [test_date, "2024-5-6", "2024-5-7"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "pay_adjustment": pay_adjustment,
        "total_bonus": total_bonus,
        "total_penalty": total_penalty,
        "results": [
            {"date": test_date, "result": "error", "reason": "activity_already_finished"},
            {"date": "2024-5-6", "result": "success", "status": "failure", "bonus": 0.0, "penalty": 0.35},
            {"date": "2024-5-7", "result": "success", "status": "success", "bonus": 0.81, "penalty": 0.0}
        ]
    }


def test_finish_multi_activity_with_invalid_data(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    # 年が不正
    data = {
        "dates": ["20241-5-5"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        'detail': "年は2024~2099の範囲で入力してください"
    }

    # 月が不正
    data = {
        "dates": ["2024-15-5"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "月は1~12の範囲で入力してください"
    }

    # 日付が不正
    data = {
        "dates": ["2024-5-50"]
    }
    response = client.put("/activities/multi/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        'detail': '日付が不正です'
    }


def test_finish_multi_acitivity_with_no_dates(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合に日付が指定されていない場合 """
    response = client.put("/activities/multi/finish",
                          json={},
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "入力データが不足しています"}


def test_get_day_activities_registered_target(client, get_resource_owner_headers):
    """ 目標時間登録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    response = client.get(f"/activities{test_date_path}",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"date": test_date,
                               "target_time": 5.0,
                               "actual_time": 0.0,
                               "status": "pending",
                               "bonus": 0.0,
                               "penalty": test_penalty}


def test_get_day_activities_registered_actual(client, get_resource_owner_headers):
    """ 活動時間登録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    response = client.get(f"/activities{test_date_path}",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"date": test_date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "status": "pending",
                               "bonus": test_bonus,
                               "penalty": 0.0}


def test_get_day_activities(client, get_resource_owner_headers):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    response = client.get(f"/activities{test_date_path}",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"date": test_date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "status": "success",
                               "bonus": test_bonus,
                               "penalty": 0.0}


def test_get_day_activities_before_register_activity(client, get_resource_owner_headers):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-5-10"
    response = client.get("/activities/2024/5/10",
                          headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"{date}の活動記録は未登録です"}


def test_get_day_activities_with_expired_token(client, get_resource_owner_headers):
    """ 期限の切れたトークンで特定日の状況を取得しようとした場合 """
    def mock_create_expired_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    setup_target_time_for_test(client, get_resource_owner_headers)
    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": RESOURCE_OWNER_USERNAME})
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/activities{test_date_path}",
                              headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "再度ログインしてください"}


def test_get_month_acitivities(client, get_resource_owner_headers):
    """ 月ごとの情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/2024/5",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_monthly_income,
                               "salary": test_salary,
                               "pay_adjustment": test_bonus,
                               "bonus": test_bonus,
                               "penalty": 0.0,
                               "success_days": 1,
                               "fail_days": 0,
                               "activity_list": [{"activity_id": 1,
                                                  "date": "2024-5-5",
                                                  "target_time": 5.0,
                                                  "actual_time": 5.0,
                                                  "status": "success",
                                                  "bonus": test_bonus,
                                                  "penalty": 0.0}]}


def test_get_month_acitivities_end_month(client, get_resource_owner_headers):
    """ 月ごとの情報を取得し、月の最終日も登録されていることを確認 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers, "2024-5-31")
    total_monthly_income = test_salary
    response = client.get("/activities/2024/5",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_monthly_income,
                               "salary": test_salary,
                               "pay_adjustment": 0.0,
                               "bonus": 0.0,
                               "penalty": 0.0,
                               "success_days": 0,
                               "fail_days": 1,
                               "activity_list": [{"activity_id": 1,
                                                  "date": "2024-5-31",
                                                  "target_time": 5.0,
                                                  "actual_time": 0.0,
                                                  "status": "pending",
                                                  "bonus": 0.0,
                                                  "penalty": 0.0}]}


def test_get_all_acitivities(client, get_resource_owner_headers):
    """ 対象ユーザーのすべての情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/total",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_monthly_income,
                               "salary": test_salary,
                               "pay_adjustment": test_bonus,
                               "bonus": test_bonus,
                               "penalty": 0.0,
                               "success_days": 1,
                               "fail_days": 0}


def test_get_year_acitivities(client, get_resource_owner_headers):
    """ 月ごとの情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    total_income = test_salary + test_bonus
    response = client.get("/activities/2024", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {"total_income": total_income,
                               "salary": test_salary,
                               "pay_adjustment": test_bonus,
                               "bonus": test_bonus,
                               "penalty": 0.0,
                               "success_days": 1,
                               "fail_days": 0,
                               "monthly_info": {
                                   "jan": {},
                                   "feb": {},
                                   "mar": {},
                                   "apr": {},
                                   "may": {
                                       "total_income": total_income,
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


def test_get_acitivities_with_wrong_status(client, get_resource_owner_headers):
    """ ステータス名を間違えた状態で取得 """
    response = client.get("/activities?status=pendin", headers=get_resource_owner_headers)
    assert response.status_code == 422
