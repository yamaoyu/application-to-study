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


class regenerateAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
