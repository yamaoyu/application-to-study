from datetime import date
from app.error_codes import NotFoundCode, NotAuthorizedCode
from app.services import inquiry_service

CATEGORY = "要望"
DETAIL = "問い合わせ詳細"

FIXED_TODAY = date(2026, 6, 1)
EXPECTED_DATE = FIXED_TODAY.isoformat()


class FixedDate(date):
    @classmethod
    def today(cls):
        return FIXED_TODAY


def setup_create_inquiry(client, get_resource_owner_headers):
    data = {"category": CATEGORY, "detail": DETAIL}
    client.post("/inquiries", json=data, headers=get_resource_owner_headers)


def test_create_inquiry(client, get_resource_owner_headers):
    data = {"category": CATEGORY, "detail": DETAIL}
    response = client.post("/inquiries", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "category": CATEGORY,
        "detail": DETAIL
    }


def test_create_inquiry_with_invalid_category(client, get_resource_owner_headers):
    data = {"category": "aaaaa", "detail": DETAIL}
    response = client.post("/inquiries", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
                {
                    "field": "category",
                    "code": "INVALID_CATEGORY"
                }
        ]
    }


def test_create_inquiry_without_detail(client, get_resource_owner_headers):
    data = {"category": CATEGORY, "detail": ""}
    response = client.post("/inquiries", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
                {
                    "field": "detail",
                    "code": "INVALID_VALUE"
                }
        ]
    }


def test_get_inquiry_by_general_user(client, get_resource_owner_headers):
    response = client.get("/inquiries", headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_HAVE_PERMISSION
    }


def test_get_inquiries(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers)
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


def test_get_inquiries_filter_by_month_without_year(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
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


def test_get_inquiries_filter_by_category(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers)
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


def test_get_inquiries_filter_by_category_not_found(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    response = client.get("/inquiries?category=エラー報告", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": []
    }


def test_get_inquiries_filter_by_priority(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers)
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


def test_get_inquiries_filter_by_priority_not_found(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    response = client.get("/inquiries?priority=高", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "inquiries": []
    }


def test_mark_inquiry_is_checked(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers)
    data = {"is_checked": True}
    response = client.patch("/inquiries/1", json=data, headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "category": CATEGORY,
        "detail": DETAIL,
        "date": EXPECTED_DATE,
        "is_checked": True,
        "priority": "低"
    }


def test_change_inquiry_priority(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    setup_create_inquiry(client, get_resource_owner_headers)
    data = {"priority": "高"}
    response = client.patch("/inquiries/1", json=data, headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "category": CATEGORY,
        "detail": DETAIL,
        "date": EXPECTED_DATE,
        "is_checked": False,
        "priority": "高"
    }


def test_edit_inquiry_not_found(client, get_admin_headers):
    data = {"priority": "高"}
    response = client.patch("/inquiries/999", json=data, headers=get_admin_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.INQUIRY_NOT_FOUND
    }
