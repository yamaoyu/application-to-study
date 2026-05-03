import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.user_service import UserService
from jose import jwt, JWTError, ExpiredSignatureError
from app.exceptions import NotFound, NotAuthorized, Forbidden
from functools import wraps

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service),
):
    return service.get_current_user_from_token(token)


def admin_only():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = kwargs["current_user"]["role"]
            if role == "admin":
                return func(*args, **kwargs)
            else:
                raise Forbidden(detail="管理者権限を持つユーザー以外はアクセスできません")
        return wrapper
    return decorator


def login_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = kwargs["token"]
                db = kwargs["db"]
                service = UserService(db)
                payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
                username = payload.get("sub")
                if username is None:
                    raise NotAuthorized(detail="証明書を認証できませんでした")
                user = service.get_user(username, message="ユーザーが見つかりません")
                if not user:
                    raise NotFound(detail="ユーザーが見つかりません")
                return func(*args, **kwargs)
            except ExpiredSignatureError:
                raise NotAuthorized(detail="再度ログインしてください")
            except JWTError:
                raise NotAuthorized(detail="証明書を認証できませんでした")
        return wrapper
    return decorator
