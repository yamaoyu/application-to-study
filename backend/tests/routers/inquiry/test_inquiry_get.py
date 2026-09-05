from app.error_codes import NotAuthorizedCode
import app.services.inquiry.inquiry_service as inquiry_service
from helpers.inquiry import (
    CATEGORY,
    DETAIL,
    EXPECTED_DATE,
    FixedDate,
    setup_create_inquiry,
    setup_update_priority
)


def test_get_inquiry_by_general_user(client, get_resource_owner_headers):
    """ 一般ユーザーは問い合わせを取得できない """
    response = client.get("/inquiries", headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_HAVE_PERMISSION
    }


def test_get_inquiries(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": [
            {
                "id": 1,
                "category": CATEGORY,
                "detail": DETAIL,
                "date": EXPECTED_DATE,
                "is_checked": False,
                "priority": "低"
            }
        ]
    }


def test_get_inquiries_filter_by_month_without_year(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?month=1", headers=get_admin_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "year",
                "code": "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED"
            }
        ]
    }


def test_get_inquiries_with_invalid_year(client, get_admin_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    response = client.get("/inquiries?year=2020", headers=get_admin_headers)
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


def test_get_inquiries_with_invalid_month(client, get_admin_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    response = client.get("/inquiries?year=2026&month=13", headers=get_admin_headers)
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


def test_get_inquiries_filter_by_category(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?category=要望", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": [
            {
                "id": 1,
                "category": CATEGORY,
                "detail": DETAIL,
                "date": EXPECTED_DATE,
                "is_checked": False,
                "priority": "低"
            }
        ]
    }


def test_get_inquiries_filter_by_category_not_found(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?category=エラー報告", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": []
    }


def test_get_inquiries_filter_by_priority(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?priority=低", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": [
            {
                "id": 1,
                "category": CATEGORY,
                "detail": DETAIL,
                "date": EXPECTED_DATE,
                "is_checked": False,
                "priority": "低"
            }
        ]
    }


def test_get_inquiries_filter_by_priority_not_found(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?priority=高", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": []
    }


def test_get_inquiries_filter_by_is_checked(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    """ 確認済みの問い合わせに絞って取得する """
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    setup_update_priority(client, get_admin_headers, monkeypatch)
    # 2件目の問い合わせを作成する(条件に当てはまらないダミー用)
    data = {"category": CATEGORY, "detail": DETAIL + "2"}
    client.post("/inquiries", json=data, headers=get_resource_owner_headers)
    response = client.get("/inquiries?is_checked=true", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": [
            {
                "id": 1,
                "category": CATEGORY,
                "detail": DETAIL,
                "date": EXPECTED_DATE,
                "is_checked": True,
                "priority": "高"
            }
        ]
    }


def test_get_inquiries_filter_by_not_checked(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    """ 未確認の問い合わせを取得する """
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?is_checked=false", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": [
            {
                "id": 1,
                "category": CATEGORY,
                "detail": DETAIL,
                "date": EXPECTED_DATE,
                "is_checked": False,
                "priority": "低"
            }
        ]
    }


def test_get_inquiries_filter_by_date(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    """ 日付で問い合わせを取得して範囲外は取得されない """
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    response = client.get("/inquiries?year=2026&month=7", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {"inquiries": []}
