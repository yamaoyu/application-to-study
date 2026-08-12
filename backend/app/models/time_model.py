import re
from enum import Enum
from pydantic import BaseModel, field_validator
from app.models.common_model import CheckDate
from typing import Optional


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


class RegisterTargetTime(BaseModel):
    date: str
    target_time: Optional[float] = None
    result: str
    reason: Optional[str] = None


class RegisterTargetTimeResponse(BaseModel):
    success_count: int
    error_count: int
    results: list[RegisterTargetTime]


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


class RegisterActualTime(BaseModel):
    date: str
    actual_time: Optional[float] = None
    result: str
    reason: Optional[str] = None


class RegisterActualTimeResponse(BaseModel):
    success_count: int
    error_count: int
    results: list[RegisterActualTime]


class FinishActivity(BaseModel):
    date: str
    status: Optional[Status] = None
    bonus: Optional[float] = None
    penalty: Optional[float] = None
    result: str
    reason: Optional[str] = None


class FinishActivityRequest(BaseModel):
    dates: list[str]

    @field_validator("dates")
    def validate_dates(cls, dates):
        if not dates:
            raise ValueError("日付リストが空です")

        for date_str in dates:
            year, month, day = map(int, date_str.split("-"))
            CheckDate(year=year, month=month, day=day)
        return dates


class FinishActivityResponse(BaseModel):
    success_count: int
    error_count: int
    pay_adjustment: float
    total_bonus: float
    total_penalty: float
    results: list[FinishActivity]


class ValidateStatus(BaseModel):
    status: Status


class getDayActivityResponse(BaseModel):
    activity_id: int
    date: str
    target_time: float
    actual_time: float
    status: Status
    bonus: float
    penalty: float


class OneActivity(BaseModel):
    date: str
    target_time: float
    actual_time: float
    status: Status
    bonus: float
    penalty: float


class ActivitySummary(BaseModel):
    total_income: float
    salary: float
    pay_adjustment: float
    bonus: float
    penalty: float
    success_days: int
    fail_days: int


class getMonthActivityResponse(ActivitySummary):
    activity_list: list[OneActivity] | list


class MonthlyInfo(BaseModel):
    salary: Optional[float] = None
    pay_adjustment: Optional[float] = None
    bonus: Optional[float] = None
    penalty: Optional[float] = None
    success_days: Optional[int] = None
    fail_days: Optional[int] = None


class getYearActivityResponse(ActivitySummary):
    monthly_info: dict[str, Optional[MonthlyInfo]]


class getAllActivitiesResponse(ActivitySummary):
    pass


class getActivitiesByStatusResponse(BaseModel):
    activities: list[getDayActivityResponse]
