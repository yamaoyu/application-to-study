from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime


class CheckYear(BaseModel):
    year: int

    @field_validator("year")
    def check_year(cls, year):
        if not (2024 <= year <= 2099):
            raise ValueError("年は2024~2099の範囲で入力してください")
        return year


class CheckYearMonth(CheckYear):
    month: int

    @field_validator("month")
    def check_month(cls, month):
        if not (1 <= month <= 12):
            raise ValueError("月は1~12の範囲で入力してください")
        return month


class CheckDate(CheckYearMonth):
    day: int

    @model_validator(mode="after")
    def check_day(self):
        try:
            datetime(year=self.year, month=self.month, day=self.day)
            return self
        except Exception:
            raise ValueError("日付が不正です")
