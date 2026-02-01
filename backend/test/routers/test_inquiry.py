from datetime import datetime

CATEGORY = "要望"
DETAIL = "問い合わせ詳細"


def setup_create_inquiry(client, get_resource_owner_headers):
    data = {"category": CATEGORY, "detail": DETAIL}
    client.post("/inquiries", json=data, headers=get_resource_owner_headers)


def test_create_inquiry(client, get_resource_owner_headers):
    data = {"category": CATEGORY, "detail": DETAIL}
    response = client.post("/inquiries", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 201
    assert response.json() == {
        "category": CATEGORY,
        "detail": DETAIL,
        "message": "こちらの内容で受け付けました"
    }


def test_create_inquiry_with_invalid_category(client, get_resource_owner_headers):
    data = {"category": "aaaaa", "detail": DETAIL}
    response = client.post("/inquiries", json=data, headers=get_resource_owner_headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "カテゴリは要望・エラー報告・その他から選択してください"
    }


def test_get_inquiry_by_general_user(client, get_resource_owner_headers):
    response = client.get("/inquiries", headers=get_resource_owner_headers)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "管理者権限を持つユーザー以外はアクセスできません"
    }


def test_get_inquiries(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    response = client.get("/inquiries", headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "category": CATEGORY,
            "detail": DETAIL,
            "date": datetime.today().strftime("%Y-%m-%d"),
            "is_checked": False,
            "priority": "低"
        }
    ]


def test_get_inquiries_filter_by_category(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    response = client.get("/inquiries?category=エラー報告", headers=get_admin_headers)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "カテゴリが「エラー報告」の問い合わせはありません"
    }


def test_get_inquiries_filter_by_priority(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    response = client.get("/inquiries?priority=高", headers=get_admin_headers)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "優先度が「高」の問い合わせはありません"
    }


def test_mark_inquiry_is_checked(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    data = {"is_checked": True}
    response = client.put("/inquiries/1", json=data, headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "category": CATEGORY,
        "detail": DETAIL,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "is_checked": True,
        "priority": "低"
    }


def test_change_inquiry_priority(client, get_admin_headers, get_resource_owner_headers):
    setup_create_inquiry(client, get_resource_owner_headers)
    data = {"priority": "高"}
    response = client.put("/inquiries/1", json=data, headers=get_admin_headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "category": CATEGORY,
        "detail": DETAIL,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "is_checked": False,
        "priority": "高"
    }
