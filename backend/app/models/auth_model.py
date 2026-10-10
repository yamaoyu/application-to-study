import os
from pydantic import BaseModel

ENV = os.getenv("ENV", "DEV")


class LoginUserInfo(BaseModel):
    username: str
    password: str


class LoginUserResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    must_change_password: bool


class regenerateAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
