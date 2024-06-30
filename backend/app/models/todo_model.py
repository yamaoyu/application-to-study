from pydantic import BaseModel


class Todo(BaseModel):
    action: str
