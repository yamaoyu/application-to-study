import os

from pydantic import BaseModel

ENV = os.getenv("ENV", "DEV")


class RegisterUserInfo(BaseModel):
    username: str
    password: str
    email: str | None = None


class RegisterUserResponse(BaseModel):
    username: str
    password: str
    email: str | None = None
    role: str | None = None


class ChangePasswordInfo(BaseModel):
    old_password: str
    new_password: str


class ForceChangePasswordInfo(BaseModel):
    new_password: str
