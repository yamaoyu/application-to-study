from pydantic import BaseModel


class TargetTimeIn(BaseModel):
    target_time: int


class ResponseTargetTime(TargetTimeIn):
    date: str
    message: str


class ActualTimeIn(BaseModel):
    actual_time: int


class ResponseActualTime(ResponseTargetTime):
    actual_time: int


class RegisterSalary(BaseModel):
    salary: int


class ResponseFinishActivity(ResponseActualTime):
    is_achieved: bool
