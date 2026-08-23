from helpers.activity import (
    test_salary,
    setup_monthly_income,
    setup_target_time
)


def test_activity_accepts_min_supported_date(client, get_resource_owner_headers):
    """ 最小サポート日付の2024-1-1は有効な日付として扱われる """
    salary_data = {"salary": 20}
    salary_response = client.post("/incomes/2024/1",
                                  json=salary_data,
                                  headers=get_resource_owner_headers)
    assert salary_response.status_code == 201
    target_data = {
        "activities": [
            {"date": "2024-1-1", "target_time": 5.0}
        ]
    }
    target_response = client.post("/activities/bulk-create-targets",
                                  json=target_data,
                                  headers=get_resource_owner_headers)
    assert target_response.status_code == 200
    assert target_response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "date": "2024-1-1",
                "result": "success",
                "target_time": 5.0,
                "reason": None
            }
        ]
    }


def test_activity_accepts_max_supported_date(client, get_resource_owner_headers):
    """ 最大サポート日付の2099-12-31は有効な日付として扱われる """
    salary_data = {"salary": 20}
    salary_response = client.post("/incomes/2099/12",
                                  json=salary_data,
                                  headers=get_resource_owner_headers)
    assert salary_response.status_code == 201
    target_data = {
        "activities": [
            {"date": "2099-12-31", "target_time": 5.0}
        ]
    }
    target_response = client.post("/activities/bulk-create-targets",
                                  json=target_data,
                                  headers=get_resource_owner_headers)
    assert target_response.status_code == 200
    assert target_response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "date": "2099-12-31",
                "result": "success",
                "target_time": 5.0,
                "reason": None
            }
        ]
    }


def test_activity_rejects_before_min_supported_date(client, get_resource_owner_headers):
    """ 最小サポート日付より前の日付は無効 """
    data = {
        "activities": [
            {"date": "2023-12-31", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/bulk-create-targets",
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


def test_activity_rejects_after_max_supported_date(client, get_resource_owner_headers):
    """ 最大サポート日付より後の日付は無効 """
    data = {
        "activities": [
            {"date": "2100-1-1", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/bulk-create-targets",
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


def test_activity_accepts_leap_day(client, get_resource_owner_headers):
    """ 閏年の2/29は有効な日付として扱われる """
    salary_data = {"salary": 20}
    salary_response = client.post("/incomes/2024/2",
                                  json=salary_data,
                                  headers=get_resource_owner_headers)
    assert salary_response.status_code == 201
    target_data = {
        "activities": [
            {"date": "2024-2-29", "target_time": 5.0}
        ]
    }
    target_response = client.post("/activities/bulk-create-targets",
                                  json=target_data,
                                  headers=get_resource_owner_headers)
    assert target_response.status_code == 200
    assert target_response.json() == {
        "success_count": 1,
        "error_count": 0,
        "results": [
            {
                "date": "2024-2-29",
                "result": "success",
                "target_time": 5.0,
                "reason": None
            }
        ]
    }


def test_activity_rejects_invalid_leap_day(client, get_resource_owner_headers):
    """ 閏年でない2/29は無効な日付となる """
    data = {
        "activities": [
            {"date": "2025-2-29", "target_time": 5.0}
        ]
    }
    response = client.post("/activities/bulk-create-targets",
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


def test_get_month_activities_not_contain_next_month(client, get_resource_owner_headers):
    """ 月ごとの情報を取得し、指定した次の月の1日の情報は取得されない """
    setup_monthly_income(client, get_resource_owner_headers)
    setup_target_time(client, get_resource_owner_headers)
    # 来月の情報を登録
    data = {"salary": test_salary}
    response = client.post("/incomes/2024/6",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    next_month_data = {
        "activities": [
            {"date": "2024-6-1", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/bulk-create-targets",
                           json=next_month_data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 200
    # 月を指定して取得
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
        "fail_days": 1,
        "activity_list": [
            {
                "date": "2024-5-5",
                "target_time": 5.0,
                "actual_time": 0.0,
                "status": "pending",
                "bonus": 0.0,
                "penalty": 0.0
            }
        ]
    }


def test_get_month_activities_contain_first_and_last_day(client, get_resource_owner_headers):
    """ 指定した月の1日と最終日が漏れなく取得できる """
    setup_monthly_income(client, get_resource_owner_headers)
    data = {
        "activities": [
            {"date": "2024-5-1", "target_time": 6.0},
            {"date": "2024-5-31", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/bulk-create-targets",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 200
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
        "fail_days": 2,
        "activity_list":
        [
            {
                "date": "2024-5-1",
                "target_time": 6.0,
                "actual_time": 0.0,
                "status": "pending",
                "bonus": 0.0,
                "penalty": 0.0
            },
            {
                "date": "2024-5-31",
                "target_time": 6.0,
                "actual_time": 0.0,
                "status": "pending",
                "bonus": 0.0,
                "penalty": 0.0
            }
        ]
    }


def test_get_year_activities_contain_first_and_last_day(client, get_resource_owner_headers):
    """ 年ごとの活動取得に1/1と12/31が含まれる """
    # 1/1と12/31の活動を登録
    salary_data = {"salary": test_salary}
    response = client.post("/incomes/2024/1",
                           json=salary_data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    response = client.post("/incomes/2024/12",
                           json=salary_data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    activity_data = {
        "activities": [
            {"date": "2024-1-1", "target_time": 6.0},
            {"date": "2024-12-31", "target_time": 6.0}
        ]
    }
    response = client.post("/activities/bulk-create-targets",
                           json=activity_data, headers=get_resource_owner_headers)
    assert response.status_code == 200
    response = client.get("/activities/2024", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "total_income": test_salary * 2,
        "salary": test_salary * 2,
        "pay_adjustment": 0.0,
        "bonus": 0.0,
        "penalty": 0.0,
        "success_days": 0,
        "fail_days": 2,
        "monthly_info": {
            "jan": {
                "salary": test_salary,
                "bonus": 0.0,
                "penalty": 0.0,
                "pay_adjustment": 0.0,
                "success_days": 0,
                "fail_days": 1
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
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
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
                "salary": test_salary,
                "bonus": 0.0,
                "penalty": 0.0,
                "pay_adjustment": 0.0,
                "success_days": 0,
                "fail_days": 1
            }
        }}


def test_get_year_activities_contain_only_designate_year(client, get_resource_owner_headers):
    """ 指定した年以外の活動が含まれない """
    # 翌年1/1と前年12/31の活動を登録
    salary_data = {"salary": test_salary}
    response = client.post("/incomes/2026/1",
                           json=salary_data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    response = client.post("/incomes/2024/12",
                           json=salary_data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    activity_data = {
        "activities": [
            {"date": "2026-1-1", "target_time": 6.0},
            {"date": "2024-12-31", "target_time": 6.0}
        ]
    }
    # 2025年の活動を取得
    salary_data = {"salary": test_salary}
    response = client.post("/incomes/2025/1",
                           json=salary_data, headers=get_resource_owner_headers)
    response = client.post("/activities/bulk-create-targets",
                           json=activity_data, headers=get_resource_owner_headers)
    response = client.get("/activities/2025", headers=get_resource_owner_headers)
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
                "salary": test_salary,
                "bonus": 0.0,
                "penalty": 0.0,
                "pay_adjustment": 0.0,
                "success_days": 0,
                "fail_days": 0
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
                "salary": None,
                "bonus": None,
                "penalty": None,
                "pay_adjustment": None,
                "success_days": None,
                "fail_days": None},
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
