from pydantic import BaseModel
from datetime import date


class Todo(BaseModel):
    action: str
    due: date
