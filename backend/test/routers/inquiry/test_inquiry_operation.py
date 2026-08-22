from app.error_codes import NotFoundCode, NotAuthorizedCode
from test.helpers.inquiry import CATEGORY, DETAIL, EXPECTED_DATE, setup_create_inquiry


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


def test_create_inquiries_same_inquiry_not_duplicate(client, get_resource_owner_headers, get_admin_headers, monkeypatch):
    for _ in range(2):
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


def test_mark_inquiry_is_checked(client, get_admin_headers, get_resource_owner_headers, monkeypatch):
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
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
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
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


def test_change_general_user_fail_change_inquiry_priority(client, get_resource_owner_headers, monkeypatch):
    setup_create_inquiry(client, get_resource_owner_headers, monkeypatch)
    data = {"priority": "高"}
    response = client.patch("/inquiries/1", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        "code": NotAuthorizedCode.NOT_HAVE_PERMISSION
    }


def test_edit_inquiry_not_found(client, get_admin_headers, monkeypatch):
    data = {"priority": "高"}
    response = client.patch("/inquiries/999", json=data, headers=get_admin_headers)
    assert response.status_code == 404
    assert response.json() == {
        "code": NotFoundCode.INQUIRY_NOT_FOUND
    }
