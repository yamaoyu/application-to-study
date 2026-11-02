from enum import StrEnum

from pydantic import BaseModel, field_validator

from app.models.common_model import CheckDate


class Status(StrEnum):
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

    @field_validator("date")
    def validate_date(cls, v):
        year, month, day = map(int, v.split("-"))
        CheckDate(year=year, month=month, day=day)
        return v


class MultiTargetTimeIn(BaseModel):
    activities: list[TargetTimeIn]

    @field_validator("activities")
    def validate_activities(cls, activities):
        if not activities:
            raise ValueError("登録する活動時間の指定がありません")

        return activities


class RegisterTargetTime(BaseModel):
    date: str
    target_time: float | None = None
    result: str
    reason: str | None = None


class RegisterTargetTimeResponse(BaseModel):
    success_count: int
    error_count: int
    results: list[RegisterTargetTime]


class ActualTimeIn(BaseModel):
    actual_time: float
    date: str

    @field_validator("date")
    def validate_date(cls, v):
        year, month, day = map(int, v.split("-"))
        CheckDate(year=year, month=month, day=day)
        return v


class MultiActualTimeIn(BaseModel):
    activities: list[ActualTimeIn]

    @field_validator("activities")
    def validate_activities(cls, activities):
        if not activities:
            raise ValueError("登録する目標時間の指定がありません")

        return activities


class RegisterActualTime(BaseModel):
    date: str
    actual_time: float | None = None
    result: str
    reason: str | None = None


class RegisterActualTimeResponse(BaseModel):
    success_count: int
    error_count: int
    results: list[RegisterActualTime]


class FinishActivity(BaseModel):
    date: str
    status: Status | None = None
    bonus: float | None = None
    penalty: float | None = None
    result: str
    reason: str | None = None


class FinishActivityRequest(BaseModel):
    dates: list[str]

    @field_validator("dates")
    def validate_dates(cls, dates):
        if not dates:
            raise ValueError("終了する日付が指定されていません")

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
    salary: float | None = None
    pay_adjustment: float | None = None
    bonus: float | None = None
    penalty: float | None = None
    success_days: int | None = None
    fail_days: int | None = None


class getYearActivityResponse(ActivitySummary):
    monthly_info: dict[str, MonthlyInfo | None]


class getAllActivitiesResponse(ActivitySummary):
    pass


class getActivitiesByStatusResponse(BaseModel):
    activities: list[getDayActivityResponse]
