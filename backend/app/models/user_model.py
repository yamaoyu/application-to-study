from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserInfo(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class ResponseCreatedUser(UserInfo):
    model_config = ConfigDict(from_attributes=True)
    message: str
