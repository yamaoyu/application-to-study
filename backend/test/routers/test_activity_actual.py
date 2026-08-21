from helpers.activity import (
    test_date,
    setup_target_time,
    setup_actual_time,
    setup_finish_activity,
    setup_monthly_income
)
from app.error_codes import NotFoundCode, ConflictCode


def test_register_actual(client, get_resource_owner_headers):
    """ 1つの活動時間を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    # 活動時間を登録
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "date": test_date,
                "result": "success",
                "actual_time": 5.0,
                "reason": None
            }
        ]
    }


def test_register_multi_actual(client, get_resource_owner_headers):
    """ 複数の活動時間を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    # 目標時間を複数登録
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    client.post("/activities/bulk-create-targets",
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
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 3,
        "error_count": 0,
        "results": [
            {
                "date": test_date,
                "result": "success",
                "actual_time": 5.0,
                "reason": None
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "actual_time": 6.0,
                "reason": None
            },
            {
                "date": "2024-5-7",
                "result": "success",
                "actual_time": 7.0,
                "reason": None
            }
        ]
    }


def test_register_multi_target_with_vacant_activities(client, get_resource_owner_headers):
    """ 複数の目標時間を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": []
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "VACANT_ACTIVITIES",
                "field": "activities"
            }
        ]
    }


def test_register_actual_with_partial_error(client, get_resource_owner_headers):
    """ 目標時間が登録されていないものが含まれる場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
            {"date": "2024-5-11", "actual_time": 5.0}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 1,
        "results": [
            {
                "date": test_date,
                "result": "success",
                "actual_time": 5.0,
                "reason": None
            },
            {
                "date": "2024-5-11",
                "result": "error",
                "actual_time": None,
                "reason": NotFoundCode.ACTIVITY_NOT_FOUND
            }
        ]
    }


def test_register_actual_with_all_errors(client, get_resource_owner_headers):
    """ 全てのリクエストがエラーになる場合 """
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
            {"date": "2024-5-11", "actual_time": 5.0}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 2,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "actual_time": None,
                "reason": NotFoundCode.SALARY_NOT_FOUND
            },
            {
                "date": "2024-5-11",
                "result": "error",
                "actual_time": None,
                "reason": NotFoundCode.SALARY_NOT_FOUND
            }
        ]
    }


def test_register_actual_with_invalid_hour(client, get_resource_owner_headers):
    """ 時間を1x.0or5、もしくはx.0or5の形で入力していない場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-10", "actual_time": 5.2}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "actual_time"
            }
        ]
    }


def test_register_actual_accept_min_hour(client, get_resource_owner_headers):
    """ 活動時間の最小値を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 0.0}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "date": test_date,
                "result": "success",
                "actual_time": 0.0,
                "reason": None
            }
        ]
    }


def test_register_actual_deny_negative_hour(client, get_resource_owner_headers):
    """ 活動時間の負の値を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": -1.0}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "actual_time"
            }
        ]
    }


def test_register_actual_accept_max_hour(client, get_resource_owner_headers):
    """ 活動時間の最大値を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 12.0}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "date": test_date,
                "result": "success",
                "actual_time": 12.0,
                "reason": None
            }
        ]
    }


def test_register_actual_deny_over_max_hour(client, get_resource_owner_headers):
    """ 活動時間の最大値を超える値を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 12.5}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "actual_time"
            }
        ]
    }


def test_register_actual_after_finish(client, get_resource_owner_headers):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 1,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "actual_time": None,
                "reason": ConflictCode.ACTIVITY_ALREADY_FINISHED
            }
        ]
    }


def test_register_multi_actual_with_invalid_hour(client, get_resource_owner_headers):
    """ 複数の活動時間を登録する際に不正なデータが含まれている場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    # 活動時間を登録
    data = {
        "activities": [
            {"date": test_date, "actual_time": 15.0}  # 上限を超える活動時間
        ]
    }
    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "actual_time"
            }
        ]
    }


def test_register_multi_actual_with_invalid_year(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "20240-5-5", "actual_time": 5.0}
        ]
    }

    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_YEAR",
                "field": "year"
            }
        ]
    }


def test_register_multi_actual_with_invalid_month(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2025-50-5", "actual_time": 5.0}
        ]
    }

    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_MONTH",
                "field": "month"
            }
        ]
    }


def test_register_multi_actual_with_invalid_date(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-50", "actual_time": 5.0}
        ]
    }

    response = client.patch("/activities/bulk-update-actuals",
                            json=data,
                            headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_DATE",
                "field": "date"
            }
        ]
    }
