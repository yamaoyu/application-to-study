import os
from pydantic import BaseModel
from typing import Optional

ENV = os.getenv("ENV", "DEV")


class RegisterUserInfo(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class RegisterUserResponse(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = None


class ChangePasswordInfo(BaseModel):
    old_password: str
    new_password: str
