from pydantic import BaseModel
from datetime import date


class TimeIn(BaseModel):
    hour: int


class RegisterSalary(BaseModel):
    salary: int


class Sample(BaseModel):
    date: date
    target: int
    study: int
    is_achieved: bool
