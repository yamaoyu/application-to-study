from app.dependencies.auth import get_current_active_user
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.admin_model import (
    StatusChangeIn,
    StatusChangeResponse,
    GetUsersIn,
    RoleChangeResponse,
    RoleChangeIn,
    ResetPasswordResponse)
from fastapi import APIRouter, Depends
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden
from app.services.admin.change_user_status import ChangeUserStatus
from app.services.admin.get_user_list import GetUserList
from app.services.admin.change_role import ChangeUserRole
from app.services.admin.reset_password import ResetPassword

router = APIRouter(prefix="/admin", tags=["admin"])


def get_change_status_service(db: Session = Depends(get_db)) -> ChangeUserStatus:
    return ChangeUserStatus(db)


def get_user_list_service(db: Session = Depends(get_db)) -> GetUserList:
    return GetUserList(db)


def get_change_role_service(db: Session = Depends(get_db)) -> ChangeUserRole:
    return ChangeUserRole(db)


def get_reset_password_service(db: Session = Depends(get_db)) -> ResetPassword:
    return ResetPassword(db)


def check_user_is_admin(role):
    if role != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)


@router.patch("/users/{username}/status", response_model=StatusChangeResponse, status_code=200)
def change_status(param: StatusChangeIn,
                  username: str,
                  current_user: dict = Depends(get_current_active_user),
                  service: ChangeUserStatus = Depends(get_change_status_service)) -> StatusChangeResponse:
    check_user_is_admin(current_user["role"])
    return service.execute(param.status, username)


@router.get("/users", status_code=200)
def get_users(params: GetUsersIn = Depends(),
              current_user: dict = Depends(get_current_active_user),
              service: GetUserList = Depends(get_user_list_service)):
    check_user_is_admin(current_user["role"])
    return service.execute(
        status=params.status,
        last_active_at=params.last_active_at,
        created_at=params.created_at,
        role=params.role,
        username=params.username,
    )


@router.patch("/users/{username}/role", response_model=RoleChangeResponse, status_code=200)
def change_role(param: RoleChangeIn,
                username: str,
                current_user: dict = Depends(get_current_active_user),
                service: ChangeUserRole = Depends(get_change_role_service)) -> RoleChangeResponse:
    check_user_is_admin(current_user["role"])
    return service.execute(param.role, username)


@router.patch("/users/{username}/password", response_model=ResetPasswordResponse, status_code=200)
def reset_password(username: str,
                   current_user: dict = Depends(get_current_active_user),
                   service: ResetPassword = Depends(get_reset_password_service)) -> ResetPasswordResponse:
    check_user_is_admin(current_user["role"])
    return service.execute(username)
