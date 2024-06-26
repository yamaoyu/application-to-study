from pydantic import BaseModel


class DateIn(BaseModel):
    date: str


class TargetTimeIn(BaseModel):
    date: str
    target_time: int


class ResponseTargetTime(TargetTimeIn):
    message: str


class ActualTimeIn(BaseModel):
    date: str
    actual_time: int


class ResponseStudyTime(ActualTimeIn):
    target_time: int
    message: str


class RegisterSalary(BaseModel):
    salary: int
