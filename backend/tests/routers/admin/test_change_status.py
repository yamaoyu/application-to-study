import asyncio
from datetime import datetime

import pytest

from app.error_codes import ConflictCode, NotAuthorizedCode, NotFoundCode
from app.security.token import create_access_token
from db.db_model import User
from tests.testdata import ADMIN_USERNAME

GENERAL_ACTIVE = "general-active"
GENERAL_SUSPEND = "general-suspend"
ADMIN_ACTIVE = "admin-active"
ADMIN_SUSPEND = "admin-suspend"


@pytest.fixture
def setup_users(db_session):
    now = datetime.now()
    users = [
        User(
            username=GENERAL_ACTIVE,
            password="dummy-Password1",
            status="active",
            role="general",
            created_at=now,
            last_active_at=now,
        ),
        User(
            username=GENERAL_SUSPEND,
            password="dummy-Password1",
            status="suspended",
            role="general",
            created_at=now,
            last_active_at=now,
        ),
        User(
            username=ADMIN_ACTIVE,
            password="dummy-Password1",
            status="active",
            role="admin",
            created_at=now,
            last_active_at=now,
        ),
        User(
            username=ADMIN_SUSPEND,
            password="dummy-Password1",
            status="suspended",
            role="admin",
            created_at=now,
            last_active_at=now,
        ),
    ]

    db_session.add_all(users)
    db_session.commit()

    return users


def test_change_user_status_active_to_suspend(client, get_admin_headers, setup_users):
    data = {"status": "suspended"}
    response = client.patch(
        f"/admin/users/{GENERAL_ACTIVE}/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"username": GENERAL_ACTIVE, "status": "suspended"}


def test_change_user_status_suspend_to_active(client, get_admin_headers, setup_users):
    data = {"status": "active"}
    response = client.patch(
        f"/admin/users/{GENERAL_SUSPEND}/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"username": GENERAL_SUSPEND, "status": "active"}


def test_general_user_fail_to_change_status(
    client, get_resource_owner_headers, setup_users
):
    data = {"status": "active"}
    response = client.patch(
        f"/admin/users/{GENERAL_ACTIVE}/status",
        json=data,
        headers=get_resource_owner_headers,
    )
    assert response.status_code == 403
    assert response.json() == {"code": NotAuthorizedCode.NOT_HAVE_PERMISSION}


def test_fail_when_not_acceptable_status(client, get_admin_headers, setup_users):
    data = {"status": "INVALID"}
    response = client.patch(
        f"/admin/users/{GENERAL_ACTIVE}/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "errors": [
            {
                "field": "status",
                "code": "INVALID_INPUT",
            },
        ],
    }


def test_fail_change_not_existing_user_status(client, get_admin_headers, setup_users):
    data = {"status": "active"}
    response = client.patch(
        "/admin/users/not-exists/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 404
    assert response.json() == {"code": NotFoundCode.USER_NOT_FOUND}


def test_change_status_with_same_status(client, get_admin_headers, setup_users):
    "現在と同じステータスを指定されても成功とする"
    data = {"status": "active"}
    response = client.patch(
        f"/admin/users/{GENERAL_ACTIVE}/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"username": GENERAL_ACTIVE, "status": "active"}


def test_fail_change_last_admin_to_suspend(client, get_admin_headers, setup_users):
    data = {"status": "suspended"}
    client.patch(
        f"/admin/users/{ADMIN_ACTIVE}/status", json=data, headers=get_admin_headers
    )
    # テストDBにはADMIN_USERNAMEしかadminユーザーがないはず
    response = client.patch(
        f"/admin/users/{ADMIN_USERNAME}/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 409
    assert response.json() == {"code": ConflictCode.LAST_ADMIN_USER}


def test_suspended_user_cannot_change_status(
    client, get_suspended_user_headers, setup_users
):
    data = {"status": "active"}
    response = client.patch(
        f"/admin/users/{GENERAL_ACTIVE}/status",
        json=data,
        headers=get_suspended_user_headers,
    )
    assert response.status_code == 403
    assert response.json() == {"code": NotAuthorizedCode.USER_SUSPENDED}


def test_change_suspended_admin_status_accepted(client, get_admin_headers, setup_users):
    """
    ロール変更時はadminロールでactiveなユーザーが0人にならないことが条件である
    activeなadminが一人だけでもsuspendedユーザーのロール変更に影響がないことを確認する
    """
    data = {"status": "active"}
    response = client.patch(
        f"/admin/users/{ADMIN_SUSPEND}/status", json=data, headers=get_admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"username": ADMIN_SUSPEND, "status": "active"}


@pytest.mark.asyncio
async def test_concurrent_change_status(
    async_client,
    create_admin,
    setup_users,
):
    """
    同時にリクエストが来た場合、activeなadminユーザーが0人にならないことを確認する
    conftestで作成したadminユーザーとsetup_usersで作成したadminユーザーの2人がいる状態で、同時に2人のadminユーザーをsuspendedにするリクエストを送る
    どちらか一方のリクエストは成功し、もう一方のリクエストは409 Conflictになることを確認する
    """
    access_token = create_access_token(
        {
            "sub": ADMIN_USERNAME,
            "role": "admin",
            "token_version": 1,
        }
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"status": "suspended"}

    response1, response2 = await asyncio.gather(
        async_client.patch(
            f"/admin/users/{ADMIN_ACTIVE}/status",
            json=data,
            headers=headers,
        ),
        async_client.patch(
            f"/admin/users/{ADMIN_USERNAME}/status",
            json=data,
            headers=headers,
        ),
    )

    assert sum(1 for r in [response1, response2] if r.status_code == 200) == 1
    assert sum(1 for r in [response1, response2] if r.status_code in [409, 403]) == 1
