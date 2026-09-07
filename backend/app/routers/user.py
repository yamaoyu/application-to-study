from app.dependencies.auth import get_current_user
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.user_model import (RegisterUserInfo,
                                   RegisterUserResponse,
                                   ChangePasswordInfo)
from fastapi import APIRouter, Depends
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden
from app.services.user.create_user import CreateUserUseCase
from app.services.user.change_password import ChangePasswordUseCase


router = APIRouter()


def get_create_user_service(db: Session = Depends(get_db)) -> CreateUserUseCase:
    return CreateUserUseCase(db)


def get_change_password_service(db: Session = Depends(get_db)) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(db)


@router.post("/users", response_model=RegisterUserResponse, status_code=201)
def create_user(user: RegisterUserInfo,
                service: CreateUserUseCase = Depends(get_create_user_service)):
    return service.execute(user.username, user.password, user.email, "general")


@router.post("/admins", response_model=RegisterUserResponse, status_code=201)
def create_admin_user(user: RegisterUserInfo,
                      current_user: dict = Depends(get_current_user),
                      service: CreateUserUseCase = Depends(get_create_user_service)):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    return service.execute(user.username, user.password, user.email, "admin")


@router.patch("/password", status_code=200, response_model=None)
def change_password(params: ChangePasswordInfo,
                    current_user: dict = Depends(get_current_user),
                    service: ChangePasswordUseCase = Depends(get_change_password_service)):
    return service.execute(params.old_password, params.new_password, current_user["username"])
