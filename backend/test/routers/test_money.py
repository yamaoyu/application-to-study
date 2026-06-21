from app.error_codes import ConflictCode, NotFoundCode

# テストで使用する変数
test_year = 2024
test_month = 6
test_salary = 23.0


def setup_salary_for_test(client, get_resource_owner_headers):
    data = {"salary": test_salary,
            "year": test_year,
            "month": test_month}
    client.post(f"/incomes/{test_year}/{test_month}", json=data, headers=get_resource_owner_headers)


def test_register_income(client, get_resource_owner_headers):
    data = {"salary": test_salary}
    response = client.post(f"/incomes/{test_year}/{test_month}",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "year": test_year,
        "month": test_month,
        "salary": test_salary
    }


def test_register_income_with_string(client, get_resource_owner_headers):
    data = {"salary": "aaaaa",
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
                {
                    "field": "salary",
                    "code": "INVALID_NUMBER"
                }
        ]
    }


def test_register_income_with_invalid_year(client, get_resource_owner_headers):
    data = {"salary": 23.0}
    response = client.post(f"/incomes/9999/{test_month}",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "year",
                "code": "INVALID_YEAR"
            }
        ]
    }


def test_register_income_with_invalid_month(client, get_resource_owner_headers):
    data = {"salary": 23.0}
    response = client.post(f"/incomes/{test_year}/9999", json=data,
                           headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "month",
                "code": "INVALID_MONTH"
            }
        ]
    }


def test_register_income_already_registered(client, get_resource_owner_headers):
    """ すでに登録されている月の月収を登録しようとした場合 """
    setup_salary_for_test(client, get_resource_owner_headers)
    data = {"salary": test_salary,
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 409
    assert response.json() == {
        "code": ConflictCode.SALARY_ALREADY_EXISTS
    }


def test_register_income_with_minus_digit(client, get_resource_owner_headers):
    """ 月収をマイナスの値で登録 """
    data = {"salary": -23.0,
            "year": test_year,
            "month": test_month}
    response = client.post(f"/incomes/{test_year}/{test_month}",
                           json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "salary",
                "code": "INVALID_VALUE"
            }
        ]
    }


def test_get_income(client, get_resource_owner_headers):
    setup_salary_for_test(client, get_resource_owner_headers)
    year = test_year
    month = test_month
    response = client.get(f"/incomes/{year}/{month}", headers=get_resource_owner_headers)
    assert response.status_code == 200
    assert response.json() == {
        "base_income": test_salary,
        "pay_adjustment": 0.0,
        "total_penalty": 0.0,
        "total_bonus": 0.0
    }


def test_get_income_without_register(client, get_resource_owner_headers):
    year = test_year
    month = test_month
    response = client.get(f"/incomes/{year}/{month}", headers=get_resource_owner_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.SALARY_NOT_FOUND_ERROR
    }


def test_get_income_with_invalid_year(client, get_resource_owner_headers):
    setup_salary_for_test(client, get_resource_owner_headers)
    month = test_month
    response = client.get(f"/incomes/9999/{month}", headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "year",
                "code": "INVALID_YEAR"
            }
        ]
    }


def test_get_income_with_invalid_month(client, get_resource_owner_headers):
    setup_salary_for_test(client, get_resource_owner_headers)
    year = test_year
    response = client.get(f"/incomes/{year}/9999", headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "month",
                "code": "INVALID_MONTH"
            }
        ]
    }


def test_get_income_by_another_user(client, get_resource_owner_headers, get_non_resource_owner_headers):
    """ 他のユーザーが登録した年収はを取得しようとした場合 """
    setup_salary_for_test(client, get_resource_owner_headers)
    user2_headers = get_non_resource_owner_headers
    year = test_year
    month = test_month
    response = client.get(f"/incomes/{year}/{month}", headers=user2_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.SALARY_NOT_FOUND_ERROR
    }
