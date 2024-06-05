from pydantic import BaseModel
from datetime import date


class DateIn(BaseModel):
    date: str


class TargetTimeIn(BaseModel):
    date: str
    target_hour: int


class ResponseTargetTime(TargetTimeIn):
    message: str


class StudyTimeIn(BaseModel):
    date: str
    study_time: int


class ResponseStudyTime(StudyTimeIn):
    target_time: int
    message: str


class RegisterSalary(BaseModel):
    salary: int


class Sample(BaseModel):
    date: date
    target: int
    study: int
    is_achieved: bool
