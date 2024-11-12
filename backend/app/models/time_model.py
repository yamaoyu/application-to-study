import re
from pydantic import BaseModel, Field, field_validator


class RegisterActivities(BaseModel):
    date: str
    target_time: float
    actual_time: float
    is_achieved: bool
    message: str


class TargetTimeIn(BaseModel):
    target_time: float

    @field_validator("target_time")
    def validate_target_time(cls, target_time):
        if not (0.5 <= target_time <= 12):
            raise ValueError("目標時間は0.5~12.0の範囲で入力してください")

        time_str = str(target_time)
        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", time_str):
            raise ValueError("目標時間は0.5時間単位で入力してください")

        return target_time


class ActualTimeIn(BaseModel):
    actual_time: float = Field(ge=0.0, le=12.0)

    @field_validator("actual_time")
    def validate_actual_time(cls, actual_time):
        if not (0.0 <= actual_time <= 12):
            raise ValueError("活動時間は0.0~12.0の範囲で入力してください")

        time_str = str(actual_time)
        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", time_str):
            raise ValueError("活動時間は0.5時間単位で入力してください")

        return actual_time


class RegisterSalary(BaseModel):
    salary: float
