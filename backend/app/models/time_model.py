from pydantic import BaseModel


class RegisterActivities(BaseModel):
    date: str
    target_time: float
    actual_time: float
    is_achieved: bool
    message: str


class TargetTimeIn(BaseModel):
    target_time: float


class ActualTimeIn(BaseModel):
    actual_time: float


class RegisterSalary(BaseModel):
    salary: float
