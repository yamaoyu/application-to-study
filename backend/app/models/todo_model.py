from pydantic import BaseModel
from datetime import datetime


class Todo(BaseModel):
    action: str
    due: datetime
