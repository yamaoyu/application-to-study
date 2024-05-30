from pydantic import BaseModel


class TimeIn(BaseModel):
    hour: int
