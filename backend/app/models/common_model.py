from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Optional


class CheckDate(BaseModel):
    year: int
    month: int
    day: Optional[int] = None

    @field_validator("year")
    def check_year(cls, year):
        if not (2024 <= year <= 2099):
            raise ValueError("年は2024年以降を入力してください")
        return year

    @field_validator("month")
    def check_month(cls, month):
        if not (1 <= month <= 12):
            raise ValueError("月は1~12の範囲で入力してください")
        return month

    @model_validator(mode="after")
    def check_day(self):
        print(self)
        if not self.day:
            return self.day
        try:
            datetime(year=self.year, month=self.month, day=self.day)
            return self.day
        except Exception:
            raise ValueError("日付が不正です")
