from pydantic import BaseModel


class UserInfo(BaseModel):
    usermail: str
    password: str
