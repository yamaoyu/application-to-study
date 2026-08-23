from unittest.mock import patch
from datetime import timedelta
from testdata import RESOURCE_OWNER_USERNAME
from lib.security import create_access_token
from helpers.activity import (
    test_bonus,
    test_penalty,
    test_date_path,
    test_salary,
    test_date,
    setup_target_time,
    setup_actual_time,
    setup_finish_activity,
    setup_monthly_income
)
from app.error_codes import NotFoundCode, NotAuthorizedCode

# --- 特定日の活動を取得 ---


def test_get_day_activities_registered_target(client, get_resource_owner_headers):
    """ 目標時間登録まで行った日の情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    response = client.get(f"/activities{test_date_path}",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "activity_id": 1,
        "date": test_date,
        "target_time": 5.0,
        "actual_time": 0.0,
        "status": "pending",
        "bonus": 0.0,
        "penalty": test_penalty
    }


def test_get_day_activities_registered_actual(client, get_resource_owner_headers):
    """ 活動時間登録まで行った日の情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    response = client.get(f"/activities{test_date_path}",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "activity_id": 1,
        "date": test_date,
        "target_time": 5.0,
        "actual_time": 5.0,
        "status": "pending",
        "bonus": test_bonus,
        "penalty": 0.0
    }


def test_get_day_activities(client, get_resource_owner_headers):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
    response = client.get(f"/activities{test_date_path}",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "activity_id": 1,
        "date": test_date,
        "target_time": 5.0,
        "actual_time": 5.0,
        "status": "success",
        "bonus": test_bonus,
        "penalty": 0.0
    }


def test_get_day_activities_before_register_activity(client, get_resource_owner_headers):
    """ 活動記録が未登録の日の情報を取得する場合 """
    response = client.get("/activities/2024/5/10",
                          headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.ACTIVITY_NOT_FOUND
    }


def test_get_day_activities_with_expired_token(client, get_resource_owner_headers):
    """ 期限の切れたトークンで特定日の状況を取得しようとした場合 """
    def mock_create_expired_access_token(data, expires_delta=timedelta(minutes=-30)):
        return create_access_token(data, expires_delta)

    setup_target_time(client, get_resource_owner_headers)
    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": RESOURCE_OWNER_USERNAME})
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/activities{test_date_path}",
                              headers=headers)
        assert response.status_code == 401
        assert response.json() == {
            "code": NotAuthorizedCode.NOT_AUTHORIZED
        }

# --- 指定した月の活動を取得 ---


def test_get_month_activities(client, get_resource_owner_headers):
    """ 月ごとの情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/2024/5",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": total_monthly_income,
        "salary": test_salary,
        "pay_adjustment": test_bonus,
        "bonus": test_bonus,
        "penalty": 0.0,
        "success_days": 1,
        "fail_days": 0,
        "activity_list": [
            {
                "date": "2024-5-5",
                "target_time": 5.0,
                "actual_time": 5.0,
                "status": "success",
                "bonus": test_bonus,
                "penalty": 0.0
            }
        ]
    }


def test_get_month_activities_when_activities_not_found(client, get_resource_owner_headers):
    """ 月収は登録されているが、活動記録がない状態で月ごとの情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    response = client.get("/activities/2024/5",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": test_salary,
        "salary": test_salary,
        "pay_adjustment": 0.0,
        "bonus": 0.0,
        "penalty": 0.0,
        "success_days": 0,
        "fail_days": 0,
        "activity_list": []
    }


def test_get_month_activities_when_salary_and_activities_not_found(client, get_resource_owner_headers):
    """ 月収も活動記録がない状態で月ごとの情報を取得 """
    response = client.get("/activities/2024/5",
                          headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.SALARY_NOT_FOUND
    }

# --- 全期間の活動取得 ---


def test_get_all_activities(client, get_resource_owner_headers):
    """ 対象ユーザーのすべての情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
    total_monthly_income = test_salary + test_bonus
    response = client.get("/activities/total",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": total_monthly_income,
        "salary": test_salary,
        "pay_adjustment": test_bonus,
        "bonus": test_bonus,
        "penalty": 0.0,
        "success_days": 1,
        "fail_days": 0
    }


def test_get_all_activities_when_activities_not_exists(client, get_resource_owner_headers):
    """ 月収は登録されているが活動記録がない場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    response = client.get("/activities/total",
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": test_salary,
        "salary": test_salary,
        "pay_adjustment": 0,
        "bonus": 0,
        "penalty": 0.0,
        "success_days": 0,
        "fail_days": 0
    }


def test_get_all_activities_when_salary_and_activities_not_exists(client, get_resource_owner_headers):
    """ 月収も活動記録も両方がない場合 """
    response = client.get("/activities/total",
                          headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.SALARY_NOT_FOUND
    }

# --- 指定した年の活動を取得 ---


def test_get_year_activities(client, get_resource_owner_headers):
    """ 年ごとの情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
    total_income = test_salary + test_bonus
    response = client.get("/activities/2024", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": total_income,
        "salary": test_salary,
        "pay_adjustment": test_bonus,
        "bonus": test_bonus,
        "penalty": 0.0,
        "success_days": 1,
        "fail_days": 0,
        "monthly_info": {
            "jan": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None
            },
            "feb": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "mar": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "apr": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "may": {
                "salary": test_salary,
                "bonus": test_bonus,
                "penalty": 0.0,
                "pay_adjustment": test_bonus,
                "success_days": 1,
                "fail_days": 0},
            "jun": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "jul": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "aug": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "sep": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "oct": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "nov": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "dec": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None}
        }}


def test_get_year_activities_when_activities_not_exists(client, get_resource_owner_headers):
    """ 月収は登録されているが活動記録がない状態で年ごとの情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    response = client.get("/activities/2024", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": test_salary,
        "salary": test_salary,
        "pay_adjustment": 0.0,
        "bonus": 0.0,
        "penalty": 0.0,
        "success_days": 0,
        "fail_days": 0,
        "monthly_info": {
            "jan": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None
            },
            "feb": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "mar": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "apr": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "may": {
                "salary": test_salary,
                "bonus": 0.0,
                "penalty": 0.0,
                "pay_adjustment": 0.0,
                "success_days": 0,
                "fail_days": 0},
            "jun": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "jul": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "aug": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "sep": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "oct": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "nov": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
            "dec": {
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None}
        }}


def test_get_year_activities_when_salary_and_activities_not_exists(client, get_resource_owner_headers):
    """ 月収は登録されているが活動記録がない状態で年ごとの情報を取得 """
    response = client.get("/activities/2024", headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.SALARY_NOT_FOUND
    }

# --- ステータスを指定して活動を取得 ---


def test_get_activities_by_status(client, get_resource_owner_headers):
    """ ステータスを指定して情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
    response = client.get("/activities?status=success", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "activities": [
            {
                "activity_id": 1,
                "date": test_date,
                "target_time": 5.0,
                "actual_time": 5.0,
                "status": "success",
                "bonus": test_bonus,
                "penalty": 0.0
            }
        ]
    }


def test_get_activities_by_status_when_no_activities(client, get_resource_owner_headers):
    """ ステータスを指定して情報を取得 """
    setup_monthly_income(client, get_resource_owner_headers)
    response = client.get("/activities?status=success", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "activities": []
    }


def test_get_activities_with_wrong_status(client, get_resource_owner_headers):
    """ ステータス名を間違えた状態で取得 """
    response = client.get("/activities?status=pendin", headers=get_resource_owner_headers)
    assert response.status_code == 422
