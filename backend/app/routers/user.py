from lib.security import get_current_user, admin_only
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.user_model import RegisterUserInfo, ResponseCreatedUser, LoginUserInfo, ChangePasswordInfo
from fastapi import APIRouter, Depends, Response, Cookie
from app.services.user_service import UserService


router = APIRouter()
response = Response()


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
          db: Session = Depends(get_db),
          device_id: str = Cookie(default=None),
          response: Response = response):
    service = get_user_service(db)
    return service.login(user_info.username, user_info.password, device_id, response)


@router.post("/logout", status_code=200)
def logout(device_id: str = Cookie(default=None),
           current_user: dict = Depends(get_current_user),
           db: Session = Depends(get_db),
           response: Response = response):
    service = get_user_service(db)
    return service.logout(current_user["username"], device_id, response)


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
