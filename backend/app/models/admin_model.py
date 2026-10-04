from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPEND = "suspended"


class UserRole(str, Enum):
    ADMIN = "admin"
    GENERAL = "general"


class StatusChangeIn(BaseModel):
    status: UserStatus


class StatusChangeResponse(BaseModel):
    username: str
    status: UserStatus


class GetUsersIn(BaseModel):
    status: Optional[UserStatus] = None
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    role: Optional[UserRole] = None
    username: Optional[str] = None


class UserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    status: UserStatus
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    role: Optional[UserRole] = None


class GetUsersResponse(BaseModel):
    users: list[UserItem]


class RoleChangeIn(BaseModel):
    role: UserRole


class RoleChangeResponse(BaseModel):
    username: str
    role: UserRole
