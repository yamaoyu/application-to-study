"""
test/routers/test_activity_xx.pyで使用する共通セットアップ
"""

# セットアップ用変数
test_salary = 23.0
test_bonus = test_penalty = 0.58
test_date_path = "/2024/5/5"
test_date = "2024-5-5"
test_year = "2024"
test_month = "5"


def setup_target_time(client, get_resource_owner_headers, target_date=test_date):
    data = {
        "activities": [
            {"date": target_date, "target_time": 5.0}
        ]
    }
    client.post("/activities/bulk-create-targets",
                json=data,
                headers=get_resource_owner_headers)


def setup_actual_time(client, get_resource_owner_headers):
    data = {
        "activities": [
            {"date": test_date, "actual_time": 5.0}
        ]
    }
    client.patch("/activities/bulk-update-actuals",
                 json=data,
                 headers=get_resource_owner_headers)


def setup_finish_activity(client, get_resource_owner_headers):
    data = {
        "dates": [test_date]
    }
    client.patch("/activities/bulk-finish",
                 json=data,
                 headers=get_resource_owner_headers)


def setup_monthly_income(client, get_resource_owner_headers):
    data = {"salary": test_salary}
    client.post(f"/incomes/{test_year}/{test_month}",
                json=data,
                headers=get_resource_owner_headers)
