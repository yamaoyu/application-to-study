from pydantic import BaseModel
from typing import Union


class RegisterActivities(BaseModel):
    date: str
    target_time: Union[float, str]
    actual_time: Union[float, str]
    is_achieved: Union[bool, str]
    message: str


class TargetTimeIn(BaseModel):
    target_time: float


class ActualTimeIn(BaseModel):
    actual_time: float


class RegisterSalary(BaseModel):
    salary: float
