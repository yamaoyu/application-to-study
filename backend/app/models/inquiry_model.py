from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator
from pydantic_core import PydanticCustomError


class Category(StrEnum):
    request = "要望"
    error = "エラー報告"
    other = "その他"


class Priority(StrEnum):
    high = "高"
    middle = "中"
    low = "低"


class CreateInquiryInput(BaseModel):
    category: str
    detail: str

    @field_validator("category")
    def validate_target_time(cls, category):
        if category not in Category:
            raise ValueError("カテゴリは要望・エラー報告・その他から選択してください")
        return category


class CreateInquiryResponse(CreateInquiryInput):
    pass


class InquiryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    detail: str
    date: date
    category: Category
    priority: Priority | None = None
    is_checked: bool | None = None


class GetInquiryResponse(BaseModel):
    inquiries: list[InquiryItem] | list


class EditInquiryInput(BaseModel):
    priority: Priority | None = None
    is_checked: bool | None = None


class InquirySearchQuery(BaseModel):
    month: int | None = None
    year: int | None = Field(default=None, validate_default=True)
    category: Category | None = None
    priority: Priority | None = None
    is_checked: bool | None = None

    @field_validator("year")
    def check_year_required_when_month_exists(cls, year, info: ValidationInfo):
        month = info.data.get("month")

        if month is not None and year is None:
            raise PydanticCustomError(
                "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED",
                "月が指定されている場合、年は必須です",
            )

        if year is not None and not (2024 <= year <= 2099):
            raise ValueError("年は2024~2099の範囲で入力してください")

        return year

    @field_validator("month")
    def check_month(cls, month):
        if month is not None and not (1 <= month <= 12):
            raise ValueError("月は1~12の範囲で入力してください")
        return month
