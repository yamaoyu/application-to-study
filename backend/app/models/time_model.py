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

    @field_validator("target_time")
    def validate_target_time(cls, target_time):
        if not (0.5 <= target_time <= 12):
            raise ValueError("目標時間は0.5~12.0の範囲で入力してください")

        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", str(target_time)):
            raise ValueError("目標時間は0.5時間単位で入力してください")

        return target_time


class MultiTargetTimeIn(BaseModel):
    activities: list

    @field_validator("activities")
    def validate_activities(cls, activities):
        for activity in activities:
            year, month, day = map(int, activity["date"].split("-"))
            CheckDate(year=year, month=month, day=day)
            TargetTimeIn(target_time=activity["target_time"])

        return activities


class ActualTimeIn(BaseModel):
    actual_time: float

    @field_validator("actual_time")
    def validate_actual_time(cls, actual_time):
        if not (0.0 <= actual_time <= 12):
            raise ValueError("活動時間は0.0~12.0の範囲で入力してください")

        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", str(actual_time)):
            raise ValueError("活動時間は0.5時間単位で入力してください")

        return actual_time


class MultiActualTimeIn(BaseModel):
    activities: list

    @field_validator("activities")
    def validate_activities(cls, activities):
        for activity in activities:
            year, month, day = map(int, activity["date"].split("-"))
            CheckDate(year=year, month=month, day=day)
            ActualTimeIn(actual_time=activity["actual_time"])

        return activities


class ValidateStatus(BaseModel):
    status: Status
