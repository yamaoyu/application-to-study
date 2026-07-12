from unittest.mock import patch
from datetime import timedelta
from testdata import RESOURCE_OWNER_USERNAME
from lib.security import create_access_token
from app.domain.activity_calculator import round_money
from app.error_codes import NotFoundCode, NotAuthorizedCode, BadRequestCode, ConflictCode

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
    client.post("/activities/target",
                json=data,
                headers=get_resource_owner_headers)


def setup_actual_time_for_test(client, get_resource_owner_headers):
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    client.put("/activities/actual",
               json=data,
               headers=get_resource_owner_headers)


def setup_finish_activity_for_test(client, get_resource_owner_headers):
    data = {
        "dates": [test_date]
    }
    client.put("/activities/finish",
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
        setup_monthly_income_for_test(client, get_resource_owner_headers)
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
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
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
    """ 入力上限の12時間を超えた目標時間を登録 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
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


def test_register_target_with_incorrect_hour(client, get_resource_owner_headers):
    """ 0.5単位でない時間を入力した場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
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
    setup_monthly_income_for_test(client, get_resource_owner_headers)
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


def test_register_target_with_invalid_month(client, get_resource_owner_headers):
    """ 存在しない月の場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
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
    """ 存在しない月の場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
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
    setup_monthly_income_for_test(client, get_resource_owner_headers)
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


def test_register_multi_with_partial_error(client, get_resource_owner_headers):
    """ 既に目標時間が登録された日が含まれる場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
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

    # 年が不正
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
    client.post("/activities/target",
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
    response = client.put("/activities/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
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


def test_register_actual_with_partial_error(client, get_resource_owner_headers):
    """ 目標時間が登録されていないものが含まれる場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0},
            {"date": "2024-5-11", "actual_time": 5.0}
        ]
    }
    response = client.put("/activities/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
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
    response = client.put("/activities/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
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
    setup_target_time_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-10", "actual_time": 5.2}
        ]
    }
    response = client.put("/activities/actual",
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
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    response = client.put("/activities/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "actual_time": None,
                "reason": ConflictCode.ACTIVITY_ALREADY_FINISHED
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
    response = client.put("/activities/actual",
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

    data = {
        "activities": [
            {"date": "20240-5-5", "actual_time": 5.0}
        ]
    }

    response = client.put("/activities/actual",
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


def test_update_already_finished_activity(client, get_resource_owner_headers):
    """ 既に終了した活動と同じ日に目標時間や活動時間を登録しようとした場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
    # 活動時間を登録する活動の中に既に終了した活動が含まれている場合
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    response = client.put("/activities/actual",
                          json=data,
                          headers=get_resource_owner_headers)
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
        "results": [
            {
                "date": test_date,
                "result": "error",
                "actual_time": None,
                "reason": ConflictCode.ACTIVITY_ALREADY_FINISHED
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
    assert response.status_code == 400
    assert response.json() == {
        "code": BadRequestCode.BULK_ACTIVITY_OPERATION_FAILED,
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


def test_finish_multi_activity_with_invalid_data(client, get_resource_owner_headers):
    """ 複数の活動を終了させた場合に不正なデータが含まれている場合 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
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


def test_get_day_activities_registered_target(client, get_resource_owner_headers):
    """ 目標時間登録まで行った日の情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
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
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
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
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
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

    setup_target_time_for_test(client, get_resource_owner_headers)
    with patch("lib.security.create_access_token", mock_create_expired_access_token):
        access_token = mock_create_expired_access_token(data={"sub": RESOURCE_OWNER_USERNAME})
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/activities{test_date_path}",
                              headers=headers)
        assert response.status_code == 401
        assert response.json() == {
            "code": NotAuthorizedCode.NOT_AUTHORIZED
        }


def test_get_month_activities(client, get_resource_owner_headers):
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
                               "activity_list": [{"date": "2024-5-5",
                                                  "target_time": 5.0,
                                                  "actual_time": 5.0,
                                                  "status": "success",
                                                  "bonus": test_bonus,
                                                  "penalty": 0.0}]}


def test_get_month_activities_end_month(client, get_resource_owner_headers):
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
                               "activity_list": [{"date": "2024-5-31",
                                                  "target_time": 5.0,
                                                  "actual_time": 0.0,
                                                  "status": "pending",
                                                  "bonus": 0.0,
                                                  "penalty": 0.0}]}


def test_get_all_activities(client, get_resource_owner_headers):
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


def test_get_year_activities(client, get_resource_owner_headers):
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


def test_get_activities_by_status(client, get_resource_owner_headers):
    """ ステータスを指定して情報を取得 """
    setup_monthly_income_for_test(client, get_resource_owner_headers)
    setup_target_time_for_test(client, get_resource_owner_headers)
    setup_actual_time_for_test(client, get_resource_owner_headers)
    setup_finish_activity_for_test(client, get_resource_owner_headers)
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


def test_get_activities_with_wrong_status(client, get_resource_owner_headers):
    """ ステータス名を間違えた状態で取得 """
    response = client.get("/activities?status=pendin", headers=get_resource_owner_headers)
    assert response.status_code == 422
