import os
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from email_validator import validate_email
from lib.security import is_password_complex, special_characters

ENV = os.getenv("ENV", "DEV")


class RegisterUserInfo(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

    @field_validator("username")
    def validate_username(cls, username):
        if not (3 <= len(username) <= 16):
            raise ValueError("ユーザー名は3文字以上、16文字以下としてください")
        return username

    @field_validator("password")
    def validate_password(cls, password):
        if not (8 <= len(password) <= 16):
            raise ValueError("パスワードは8文字以上、16文字以下としてください")
        elif not is_password_complex(password):
            raise ValueError(f"パスワードは大文字、小文字、数字、記号({special_characters})をそれぞれ1文字以上含む必要があります")
        return password

    @field_validator("email")
    def validate_email(cls, email):
        if not email:
            return None
        try:
            validate_email(email, check_deliverability=ENV == "PROD")
            return email
        except Exception:
            raise ValueError("正しい形式のメールアドレスを入力してください")


class LoginUserInfo(BaseModel):
    username: str
    password: str


class ResponseCreatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = None
    message: str


class ChangePasswordInfo(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, new_password):
        if not (8 <= len(new_password) <= 16):
            raise ValueError("パスワードは8文字以上、16文字以下としてください")
        elif not is_password_complex(new_password):
            raise ValueError(f"パスワードは大文字、小文字、数字、記号({special_characters})をそれぞれ1文字以上含む必要があります")
        return new_password
