from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import (
    get_current_active_user,
    get_current_user_for_password_change,
)
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden
from app.models.user_model import (
    ChangePasswordInfo,
    ForceChangePasswordInfo,
    RegisterUserInfo,
    RegisterUserResponse,
)
from app.services.user.change_password import ChangePasswordUseCase
from app.services.user.create_user import CreateUserUseCase
from app.services.user.force_change_password import ForceChangePasswordUseCase
from db.database import get_db

router = APIRouter()


def get_create_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> CreateUserUseCase:
    return CreateUserUseCase(db)


def get_change_password_service(
    db: Annotated[Session, Depends(get_db)],
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(db)


def get_force_change_password_service(
    db: Annotated[Session, Depends(get_db)],
) -> ForceChangePasswordUseCase:
    return ForceChangePasswordUseCase(db)


@router.post("/users", response_model=RegisterUserResponse, status_code=201)
def create_user(
    user: RegisterUserInfo,
    service: Annotated[CreateUserUseCase, Depends(get_create_user_service)],
):
    return service.execute(user.username, user.password, user.email, "general")


@router.post("/admins", response_model=RegisterUserResponse, status_code=201)
def create_admin_user(
    user: RegisterUserInfo,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    service: Annotated[CreateUserUseCase, Depends(get_create_user_service)],
):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    return service.execute(user.username, user.password, user.email, "admin")


@router.patch("/password", status_code=200, response_model=None)
def change_password(
    params: ChangePasswordInfo,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    service: Annotated[ChangePasswordUseCase, Depends(get_change_password_service)],
):
    return service.execute(
        params.old_password, params.new_password, current_user["username"]
    )


@router.patch("/password/forced", status_code=200, response_model=None)
def force_change_password(
    params: ForceChangePasswordInfo,
    current_user: Annotated[dict, Depends(get_current_user_for_password_change)],
    service: Annotated[
        ForceChangePasswordUseCase, Depends(get_force_change_password_service)
    ],
):
    return service.execute(params.new_password, current_user["username"])
