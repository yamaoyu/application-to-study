import os
from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user_for_logout
from app.models.auth_model import (
    LoginUserInfo,
    LoginUserResponse,
    regenerateAccessTokenResponse,
)
from app.services.auth.login import LoginUseCase
from app.services.auth.logout import LogoutUseCase
from app.services.auth.regenerate_access_token import RegenerateAccessTokenUseCase
from db.database import get_db

router = APIRouter()

CookieSameSite = Literal["lax", "strict", "none"]


def get_cookie_samesite() -> CookieSameSite:
    value = os.getenv("COOKIE_SAMESITE", "lax").lower()
    if value not in ("lax", "strict", "none"):
        raise ValueError("COOKIE_SAMESITE must be one of: lax, strict, none")
    return value


APP_SCHEME = os.getenv("APP_SCHEME", "http")
COOKIE_SAMESITE = get_cookie_samesite()


def get_login_service(db: Annotated[Session, Depends(get_db)]) -> LoginUseCase:
    return LoginUseCase(db)


def get_logout_service(db: Annotated[Session, Depends(get_db)]) -> LogoutUseCase:
    return LogoutUseCase(db)


def get_regenerate_access_token_service(
    db: Annotated[Session, Depends(get_db)],
) -> RegenerateAccessTokenUseCase:
    return RegenerateAccessTokenUseCase(db)


async def get_login_user_info(request: Request) -> LoginUserInfo:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith(
        ("application/x-www-form-urlencoded", "multipart/form-data")
    ):
        form = await request.form()
        return LoginUserInfo.model_validate(
            {
                "username": form.get("username"),
                "password": form.get("password"),
            }
        )

    payload = await request.json()
    return LoginUserInfo.model_validate(payload)


@router.post("/login", status_code=200, response_model=LoginUserResponse)
def login(
    response: Response,
    user_info: Annotated[LoginUserInfo, Depends(get_login_user_info)],
    service: Annotated[LoginUseCase, Depends(get_login_service)],
    device_id: str = Cookie(default=None),
):
    token_info = service.execute(user_info.username, user_info.password, device_id)
    response.set_cookie(
        key="refresh_token",
        value=token_info["refresh_token"],
        secure=APP_SCHEME.lower() == "https",
        samesite=COOKIE_SAMESITE,
        httponly=True,
        expires=token_info["expires_at"],
    )
    response.set_cookie(
        key="device_id",
        value=token_info["device_id"],
        secure=APP_SCHEME.lower() == "https",
        samesite=COOKIE_SAMESITE,
        httponly=True,
    )
    return {
        "access_token": token_info["access_token"],
        "token_type": token_info["token_type"],
        "role": token_info["role"],
        "must_change_password": token_info["must_change_password"],
    }


@router.post("/logout", status_code=200, response_model=None)
def logout(
    current_user: Annotated[dict, Depends(get_current_user_for_logout)],
    service: Annotated[LogoutUseCase, Depends(get_logout_service)],
    response: Response,
    device_id: str = Cookie(default=None),
):
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="device_id")
    return service.execute(current_user["username"], device_id)


@router.post("/token", status_code=200, response_model=regenerateAccessTokenResponse)
def regenerate_access_token(
    service: Annotated[RegenerateAccessTokenUseCase, Depends(get_regenerate_access_token_service)],
    refresh_token: str = Cookie(default=None),
    device_id: str = Cookie(default=None),
):
    """アクセストークンの期限が切れている場合、リフレッシュトークンを使ってアクセストークンを再発行する"""
    return service.execute(refresh_token, device_id)
