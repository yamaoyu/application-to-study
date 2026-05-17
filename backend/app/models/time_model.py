import re
from enum import Enum
from pydantic import BaseModel, field_validator
from app.models.common_model import CheckDate


class Status(str, Enum):
    pending = "pending"
    success = "success"
    failure = "failure"


class RegisterActivities(BaseModel):
    date: str
    target_time: float
    actual_time: float
    status: Status
    message: str


class TargetTimeIn(BaseModel):
    target_time: float
    date: str

    @field_validator("target_time")
    def validate_target_time(cls, target_time):
        if not (0.5 <= target_time <= 12):
            raise ValueError("目標時間は0.5~12.0の範囲で入力してください")

        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", str(target_time)):
            raise ValueError("目標時間は0.5時間単位で入力してください")

        return target_time

    @field_validator("date")
    def validate_date(cls, v):
        year, month, day = map(int, v.split("-"))
        CheckDate(year=year, month=month, day=day)
        return v


class MultiTargetTimeIn(BaseModel):
    activities: list[TargetTimeIn]


class ActualTimeIn(BaseModel):
    actual_time: float
    date: str

    @field_validator("actual_time")
    def validate_actual_time(cls, actual_time):
        if not (0.0 <= actual_time <= 12):
            raise ValueError("活動時間は0.0~12.0の範囲で入力してください")

        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", str(actual_time)):
            raise ValueError("活動時間は0.5時間単位で入力してください")

        return actual_time

    @field_validator("date")
    def validate_date(cls, v):
        year, month, day = map(int, v.split("-"))
        CheckDate(year=year, month=month, day=day)
        return v


class MultiActualTimeIn(BaseModel):
    activities: list[ActualTimeIn]


class MultiFinishActivityIn(BaseModel):
    dates: list[str]

    @field_validator("dates")
    def validate_dates(cls, dates):
        for date_str in dates:
            year, month, day = map(int, date_str.split("-"))
            print(year, month, day)
            CheckDate(year=year, month=month, day=day)
        return dates


class ValidateStatus(BaseModel):
    status: Status
