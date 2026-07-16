from unittest.mock import patch
from datetime import timedelta
from testdata import RESOURCE_OWNER_USERNAME
from lib.security import create_access_token
from test.helpers.activity import (
    test_date,
    setup_target_time,
    setup_monthly_income
)
from app.error_codes import NotFoundCode, NotAuthorizedCode, BadRequestCode, ConflictCode


def test_register_target(client, get_resource_owner_headers):
    """ 1つの目標時間を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "success",
                "target_time": 5.0,
                "reason": None
            }
        ]
    }


def test_register_target_without_monthly_income(client, get_resource_owner_headers):
    """ 月収が登録されていない状態で目標時間を登録しようとした場合 """
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": NotFoundCode.SALARY_NOT_FOUND,
                "target_time": None
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
        setup_monthly_income(client, get_resource_owner_headers)
        data = {
            "activities": [
                {"date": test_date, "target_time": 5.0}
            ]
        }
        response = client.post("/activities/target",
                               json=data,
                               headers=headers)
        assert response.status_code == 401
        assert response.json() == {
            "code": NotAuthorizedCode.NOT_AUTHORIZED
        }


def test_register_target_twice(client, get_resource_owner_headers):
    """ 既に目標時間が登録されている日の目標時間を登録 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "reason": ConflictCode.TARGET_TIME_ALREADY_REGISTERED,
                "target_time": None
            }
        ]
    }


def test_register_target_out_of_range(client, get_resource_owner_headers):
    """ 入力上限の12時間を超えた目標時間と入力下限の0.5を下回った目標時間を登録 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 15.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "target_time"
            }
        ]
    }
    data = {
        "activities": [
            {"date": test_date, "target_time": 0.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "target_time"
            }
        ]
    }


def test_register_target_with_incorrect_hour(client, get_resource_owner_headers):
    """ 0.5単位でない時間を入力した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-5", "target_time": 5.3}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "target_time"
            }
        ]
    }


def test_register_target_with_invalid_year(client, get_resource_owner_headers):
    """ 年が2024 <= year <= 2099ではない """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "20240-5-5", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
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
    data = {
        "activities": [
            {"date": "2023-5-5", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
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


def test_register_target_with_invalid_month(client, get_resource_owner_headers):
    """ 存在しない月の場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-13-30", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
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


def test_register_target_with_invalid_date(client, get_resource_owner_headers):
    """ 存在しない日付の場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-2-30", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
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


def test_register_multi_target(client, get_resource_owner_headers):
    """ 複数の目標時間を登録した場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 7.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": test_date,
                "result": "success",
                "target_time": 5.0,
                "reason": None
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "target_time": 6.0,
                "reason": None
            },
            {
                "date": "2024-5-7",
                "result": "success",
                "target_time": 7.0,
                "reason": None
            }
        ]
    }


def test_register_multi_target_with_partial_error(client, get_resource_owner_headers):
    """ 既に目標時間が登録された日が含まれて一部がエラーになる場合 """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "results": [
            {
                "date": "2024-5-5",
                "result": "error",
                "target_time": None,
                "reason": ConflictCode.TARGET_TIME_ALREADY_REGISTERED
            },
            {
                "date": "2024-5-6",
                "result": "success",
                "target_time": 6.0,
                "reason": None
            }
        ]
    }


def test_register_multi_target_with_all_errors(client, get_resource_owner_headers):
    """ 月収が登録されておらず、全てがエラー """
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.0},
            {"date": "2024-5-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
        "results": [
            {
                "date": "2024-5-5",
                "result": "error",
                "target_time": None,
                "reason": NotFoundCode.SALARY_NOT_FOUND
            },
            {
                "date": "2024-5-6",
                "result": "error",
                "target_time": None,
                "reason": NotFoundCode.SALARY_NOT_FOUND
            }
        ]
    }


def test_register_multi_target_with_invalid_hour(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    # 目標時間が不正
    data = {
        "activities": [
            {"date": test_date, "target_time": 5.2},
            {"date": "2024-5-6", "target_time": 6.0},
            {"date": "2024-5-7", "target_time": 15.0}
        ]
    }
    response = client.post("/activities/target",
                           json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "code": "INVALID_VALUE",
                "field": "target_time"
            },
            {
                "code": "INVALID_VALUE",
                "field": "target_time"
            }
        ]
    }


def test_register_multi_target_with_invalid_year(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    # 年が不正
    data = {
        "activities": [
            {"date": "20240-5-5", "target_time": 5.0},
            {"date": "2024-5-5", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
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


def test_register_multi_target_with_invalid_month(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-13-6", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/target",
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


def test_register_multi_target_with_invalid_date(client, get_resource_owner_headers):
    setup_monthly_income(client, get_resource_owner_headers)
    # 日付が不正
    data = {
        "activities": [
            {"date": "2024-5-35", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/target",
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
