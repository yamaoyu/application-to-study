from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class UserInfo(BaseModel):
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
        if len(email) > 0 and "@" not in email:
            raise ValueError("正しいメールアドレスを入力してください")
        return email


class ResponseCreatedUser(UserInfo):
    model_config = ConfigDict(from_attributes=True)
    message: str
