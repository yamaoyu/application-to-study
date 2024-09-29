from pydantic import BaseModel
from typing import Union


class RegisterActivities(BaseModel):
    date: str
    target_time: Union[int, str]
    actual_time: Union[int, str]
    is_achieved: Union[bool, str]
    message: str


class TargetTimeIn(BaseModel):
    target_time: int


class ActualTimeIn(BaseModel):
    actual_time: int


class RegisterSalary(BaseModel):
    salary: int
