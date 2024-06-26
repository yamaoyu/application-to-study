from pydantic import BaseModel


class TodoIn(BaseModel):
    action: str
    date: str


class UpdateAction(BaseModel):
    action: str
