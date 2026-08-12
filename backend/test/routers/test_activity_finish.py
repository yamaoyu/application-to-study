from helpers.activity import (
    test_date,
    test_bonus,
    setup_target_time,
    setup_actual_time,
    setup_finish_activity,
    setup_monthly_income
)
from app.error_codes import NotFoundCode, ConflictCode
from app.domain.activity_calculator import round_money


def test_finish_activity(client, get_resource_owner_headers):
    """ 1つの活動を終了した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    # 活動時間を登録
    data = {
        "dates": [test_date]
    }
    response = client.put("/activities/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 1,
        "error_count": 0,
        "pay_adjustment": test_bonus,
        "total_bonus": test_bonus,
        "total_penalty": 0,
        "results": [
            {
                "date": test_date,
                "result": "success",
                "status": "success",
                "bonus": 0.58,
                "penalty": 0.0,
                "reason": None
            }
        ]
    }


def test_finish_multi_activities(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合 """
    setup_monthly_income(client, get_resource_owner_headers)
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
    client.post("/activities/target",
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
    client.put("/activities/actual",
               json=data,
               headers=get_resource_owner_headers)
    # 活動を終了
    data = {
        "dates": [test_date, "2024-5-6", "2024-5-7"]
    }
    response = client.put("/activities/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 3,
        "error_count": 0,
        "pay_adjustment": pay_adjustment,
        "total_bonus": total_bonus,
        "total_penalty": total_penalty,
        "results": [
            {
                "date": "2024-5-5",
                "result": "success",
                "status": "success",
                "bonus": 0.58,
                "penalty": 0.0,
                "reason": None
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "status": "failure",
                "bonus": 0.0,
                "penalty": 0.35,
                "reason": None
            },
            {
                "date": "2024-5-7",
                "result": "success",
                "status": "success",
                "bonus": 0.81,
                "penalty": 0.0,
                "reason": None
            }
        ]
    }


def test_finish_multi_activity_with_partial_errors(client, get_resource_owner_headers):
    """ 複数の活動を終了させて一部のみエラーがある場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    setup_actual_time(client, get_resource_owner_headers)
    setup_finish_activity(client, get_resource_owner_headers)
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
    client.post("/activities/target",
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
    client.put("/activities/actual",
               json=data,
               headers=get_resource_owner_headers)
    # 活動を終了
    data = {
        "dates": [test_date, "2024-5-6", "2024-5-7"]
    }
    response = client.put("/activities/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 2,
        "error_count": 1,
        "pay_adjustment": pay_adjustment,
        "total_bonus": total_bonus,
        "total_penalty": total_penalty,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": ConflictCode.ACTIVITY_ALREADY_FINISHED,
                "bonus": None,
                "penalty": None,
                "status": None
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "status": "failure",
                "bonus": 0.0,
                "penalty": 0.35,
                "reason": None
            },
            {
                "date": "2024-5-7",
                "result": "success",
                "status": "success",
                "bonus": 0.81,
                "penalty": 0.0,
                "reason": None
            }
        ]
    }


def test_finish_multi_activity_with_all_errors(client, get_resource_owner_headers):
    """ 複数の活動を終了させて全てエラー場合 """
    # 活動を終了
    data = {
        "dates": [test_date, "2024-5-6", "2024-5-7"]
    }
    response = client.put("/activities/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "success_count": 0,
        "error_count": 3,
        "pay_adjustment": 0,
        "total_bonus": 0,
        "total_penalty": 0,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": NotFoundCode.ACTIVITY_NOT_FOUND,
                "bonus": None,
                "penalty": None,
                "status": None
            },
            {
                "date": "2024-5-6",
                "result": "error",
                "reason": NotFoundCode.ACTIVITY_NOT_FOUND,
                "bonus": None,
                "penalty": None,
                "status": None
            },
            {
                "date": "2024-5-7",
                "result": "error",
                "reason": NotFoundCode.ACTIVITY_NOT_FOUND,
                "bonus": None,
                "penalty": None,
                "status": None
            },
        ]
    }


def test_finish_multi_activity_with_invalid_year(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    # 年が不正
    data = {
        "dates": ["20241-5-5"]
    }
    response = client.put("/activities/finish",
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


def test_finish_multi_activity_with_invalid_month(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)

    # 月が不正
    data = {
        "dates": ["2024-15-5"]
    }
    response = client.put("/activities/finish",
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


def test_finish_multi_activity_with_invalid_date(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)

    # 日付が不正
    data = {
        "dates": ["2024-5-50"]
    }
    response = client.put("/activities/finish",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "dates"
            }
        ]
    }


def test_finish_multi_acitivity_with_no_dates(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合に日付が指定されていない場合 """
    response = client.put("/activities/finish",
                          json={},
                          headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "REQUIRED",
                "field": "dates"
            }
        ]
    }
