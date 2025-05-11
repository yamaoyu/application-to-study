from pydantic import BaseModel
from datetime import date


class Todo(BaseModel):
    title: str
    due: date
    detail: str
