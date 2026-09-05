from datetime import date
from app.services.inquiry import inquiry_service

CATEGORY = "要望"
DETAIL = "問い合わせ詳細"

FIXED_TODAY = date(2026, 6, 1)
EXPECTED_DATE = FIXED_TODAY.isoformat()


class FixedDate(date):
    """ 期待値を固定するために日付を固定するクラス """
    @classmethod
    def today(cls):
        return FIXED_TODAY


def setup_create_inquiry(client, get_resource_owner_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    data = {"category": CATEGORY, "detail": DETAIL}
    client.post("/inquiries", json=data, headers=get_resource_owner_headers)


def setup_update_priority(client, get_admin_headers, monkeypatch):
    monkeypatch.setattr(inquiry_service, "date", FixedDate)
    data = {"priority": "高", "is_checked": True}
    client.patch("/inquiries/1", json=data, headers=get_admin_headers)
