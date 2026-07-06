import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.user_service import UserService
from app.exceptions import Forbidden
from functools import wraps
from app.error_codes import NotAuthorizedCode

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
                raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
        return wrapper
    return decorator
