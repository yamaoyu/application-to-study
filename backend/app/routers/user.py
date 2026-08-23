import os
from app.dependencies.auth import get_current_user
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.user_model import (RegisterUserInfo,
                                   RegisterUserResponse,
                                   LoginUserInfo,
                                   LoginUserResponse,
                                   regenerateAccessTokenResponse,
                                   ChangePasswordInfo)
from fastapi import APIRouter, Depends, Response, Cookie, Request
from app.services.user_service import UserService
from typing import Literal
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden

CookieSameSite = Literal["lax", "strict", "none"]


def get_cookie_samesite() -> CookieSameSite:
    value = os.getenv("COOKIE_SAMESITE", "lax").lower()
    if value not in ("lax", "strict", "none"):
        raise ValueError("COOKIE_SAMESITE must be one of: lax, strict, none")
    return value


APP_SCHEME = os.getenv("APP_SCHEME", "http")
COOKIE_SAMESITE = get_cookie_samesite()

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


async def get_login_user_info(request: Request) -> LoginUserInfo:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith(("application/x-www-form-urlencoded", "multipart/form-data")):
        form = await request.form()
        return LoginUserInfo.model_validate({
            "username": form.get("username"),
            "password": form.get("password"),
        })

    payload = await request.json()
    return LoginUserInfo.model_validate(payload)


@router.post("/users", response_model=RegisterUserResponse, status_code=201)
def create_user(user: RegisterUserInfo, db: Session = Depends(get_db)):
    service = get_user_service(db)
    return service.create_user(user.username, user.password, user.email, "general")


@router.post("/admins", response_model=RegisterUserResponse, status_code=201)
def create_admin_user(user: RegisterUserInfo,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    service = get_user_service(db)
    return service.create_user(user.username, user.password, user.email, "admin")


@router.post("/login", status_code=200, response_model=LoginUserResponse)
def login(response: Response,
          user_info: LoginUserInfo = Depends(get_login_user_info),
          db: Session = Depends(get_db),
          device_id: str = Cookie(default=None)):
    service = get_user_service(db)
    token_info = service.login(user_info.username, user_info.password, device_id)
    response.set_cookie(
        key="refresh_token",
        value=token_info["refresh_token"],
        secure=APP_SCHEME.lower() == "https",
        samesite=COOKIE_SAMESITE,
        httponly=True,
        expires=token_info["expires_at"])
    response.set_cookie(
        key="device_id",
        value=token_info["device_id"],
        secure=APP_SCHEME.lower() == "https",
        samesite=COOKIE_SAMESITE,
        httponly=True)
    return {
        "access_token": token_info["access_token"],
        "token_type": token_info["token_type"],
        "role": token_info["role"]
    }


@router.post("/logout", status_code=200, response_model=None)
def logout(response: Response,
           device_id: str = Cookie(default=None),
           current_user: dict = Depends(get_current_user),
           db: Session = Depends(get_db)):
    service = get_user_service(db)
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="device_id")
    return service.logout(current_user["username"], device_id)


@router.post("/token", status_code=200, response_model=regenerateAccessTokenResponse)
def regenerate_access_token(refresh_token: str = Cookie(default=None),
                            device_id: str = Cookie(default=None),
                            db: Session = Depends(get_db)):
    """ アクセストークンの期限が切れている場合、リフレッシュトークンを使ってアクセストークンを再発行する """
    service = get_user_service(db)
    return service.regenerate_access_token(refresh_token, device_id)


@router.patch("/password", status_code=200, response_model=None)
def change_password(params: ChangePasswordInfo,
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    service = get_user_service(db)
    return service.change_password(params.old_password, params.new_password, current_user["username"])
