from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class Status(str, Enum):
    ACTIVE = "active"
    SUSPEND = "suspended"


class Role(str, Enum):
    ADMIN = "admin"
    GENERAL = "general"


class StatusChangeIn(BaseModel):
    status: Status


class StatusChangeResponse(BaseModel):
    username: str
    status: Status


class GetUsersIn(BaseModel):
    status: Optional[Status] = None
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    role: Optional[Role] = None
    username: Optional[str] = None


class UserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    status: Status
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    role: Optional[Role] = None


class GetUsersResponse(BaseModel):
    users: list[UserItem]
