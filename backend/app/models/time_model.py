from pydantic import BaseModel, Field


class RegisterActivities(BaseModel):
    date: str
    target_time: float = Field(ge=0.5, le=12.5)
    actual_time: float = Field(ge=0.0, le=12.5)  # 目標時間設定時は0が入るため
    is_achieved: bool
    message: str


class TargetTimeIn(BaseModel):
    target_time: float


class ActualTimeIn(BaseModel):
    actual_time: float


class RegisterSalary(BaseModel):
    salary: float
