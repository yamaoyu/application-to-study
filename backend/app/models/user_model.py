from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from email_validator import validate_email


class RegisterUserInfo(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = None

    @field_validator("username")
    def validate_username(cls, username):
        if not (3 <= len(username) <= 16):
            raise ValueError("ユーザー名は3文字以上、16文字以下としてください")
        return username

    @field_validator("password")
    def validate_password(cls, password):
        if not (8 <= len(password) <= 16):
            raise ValueError("パスワードは8文字以上、16文字以下としてください")
        return password

    @field_validator("email")
    def validate_email(cls, email):
        try:
            validate_email(email)
            return email
        except Exception:
            raise ValueError("正しい形式のメールアドレスを入力してください")


class LoginUserInfo(BaseModel):
    username: str
    password: str
    device: str


class ResponseCreatedUser(RegisterUserInfo):
    model_config = ConfigDict(from_attributes=True)
    message: str


class DeviceInfo(BaseModel):
    device: str
