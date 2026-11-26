from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.user.active_admin_policy import UserRole, UserStatus


class StatusChangeIn(BaseModel):
    status: UserStatus


class StatusChangeResponse(BaseModel):
    username: str
    status: UserStatus


class GetUsersIn(BaseModel):
    status: UserStatus | None = None
    last_active_at: datetime | None = None
    created_at: datetime | None = None
    role: UserRole | None = None
    username: str | None = None


class UserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    status: UserStatus
    last_active_at: datetime | None = None
    created_at: datetime | None = None
    role: UserRole | None = None


class GetUsersResponse(BaseModel):
    users: list[UserItem]


class RoleChangeIn(BaseModel):
    role: UserRole


class RoleChangeResponse(BaseModel):
    username: str
    role: UserRole


class ResetPasswordResponse(BaseModel):
    username: str
    password: str
