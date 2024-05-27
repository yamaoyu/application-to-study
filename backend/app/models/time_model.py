from pydantic import BaseModel


class RegisterTime(BaseModel):
    hour: int
