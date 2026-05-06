import os
from app.dependencies.auth import get_current_user, admin_only
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.user_model import RegisterUserInfo, ResponseCreatedUser, LoginUserInfo, ChangePasswordInfo
from fastapi import APIRouter, Depends, Response, Cookie
from app.services.user_service import UserService

APP_SCHEME = os.getenv("APP_SCHEME")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE")

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("/users", response_model=ResponseCreatedUser, status_code=201)
def create_user(user: RegisterUserInfo, db: Session = Depends(get_db)):
    service = get_user_service(db)
    return service.create_user(user.username, user.password, user.email, "general")


@router.post("/admins", response_model=ResponseCreatedUser, status_code=201)
@admin_only()
def create_admin_user(user: RegisterUserInfo,
                      db: Session = Depends(get_db)):
    service = get_user_service(db)
    return service.create_user(user.username, user.password, user.email, "admin")


@router.post("/login", status_code=200)
def login(user_info: LoginUserInfo,
          response: Response,
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


@router.post("/logout", status_code=200)
def logout(device_id: str = Cookie(default=None),
           response: Response = None,
           current_user: dict = Depends(get_current_user),
           db: Session = Depends(get_db)):
    service = get_user_service(db)
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="device_id")
    return service.logout(current_user["username"], device_id)


@router.post("/token", status_code=200)
def regenerate_access_token(refresh_token: str = Cookie(default=None),
                            device_id: str = Cookie(default=None),
                            db: Session = Depends(get_db)):
    """ アクセストークンの期限が切れている場合、リフレッシュトークンを使ってアクセストークンを再発行する """
    service = get_user_service(db)
    return service.regenerate_access_token(refresh_token, device_id)


@router.put("/password", status_code=200)
def change_password(params: ChangePasswordInfo,
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    service = get_user_service(db)
    return service.change_password(params.old_password, params.new_password, current_user["username"])
