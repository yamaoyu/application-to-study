from app.dependencies.auth import get_current_user
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.admin_model import StatusChangeIn, StatusChangeResponse, GetUsersIn
from fastapi import APIRouter, Depends
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden
from app.services.admin.change_user_status import ChangeUserStatus
from app.services.admin.get_user_list import GetUserList

router = APIRouter(prefix="/admin", tags=["admin"])


def get_change_status_service(db: Session = Depends(get_db)) -> ChangeUserStatus:
    return ChangeUserStatus(db)


def get_user_list_service(db: Session = Depends(get_db)) -> GetUserList:
    return GetUserList(db)


def check_user_is_admin(role):
    if role != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)


@router.patch("/users/{username}/status", response_model=StatusChangeResponse, status_code=201)
def change_status(param: StatusChangeIn,
                  current_user: dict = Depends(get_current_user),
                  service: ChangeUserStatus = Depends(get_change_status_service)) -> StatusChangeResponse:
    check_user_is_admin(current_user["role"])
    return service.execute(param.status, current_user["username"])


@router.get("/users", status_code=200)
def get_users(params: GetUsersIn = Depends(),
              current_user: dict = Depends(get_current_user),
              service: GetUserList = Depends(get_user_list_service)):
    check_user_is_admin(current_user["role"])
    return service.execute(
        status=params.status,
        last_active_at=params.last_active_at,
        created_at=params.created_at,
        role=params.role,
        username=params.username,
    )
