from enum import Enum
from pydantic import BaseModel, field_validator, ConfigDict, ValidationInfo, Field
from typing import Optional
from datetime import date
from pydantic_core import PydanticCustomError


class Category(str, Enum):
    request = "要望"
    error = "エラー報告"
    other = "その他"


class Priority(str, Enum):
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

    @field_validator("detail")
    def check_detail_length(cls, detail):
        if detail is None or not detail.strip():
            raise ValueError("詳細は必須です")
        if len(detail) > 256:
            raise ValueError("詳細は256文字以内で入力してください")
        return detail


class CreateInquiryResponse(CreateInquiryInput):
    pass


class InquiryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    detail: str
    date: date
    category: Category
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None


class GetInquiryResponse(BaseModel):
    inquiries: list[InquiryItem] | list


class EditInquiryInput(BaseModel):
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None


class InquirySearchQuery(BaseModel):
    month: Optional[int] = None
    year: Optional[int] = Field(default=None, validate_default=True)
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None

    @field_validator("year")
    def check_year_required_when_month_exists(cls, year, info: ValidationInfo):
        month = info.data.get("month")

        if month is not None and year is None:
            raise PydanticCustomError(
                "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED",
                "月が指定されている場合、年は必須です"
            )

        if year is not None and not (2024 <= year <= 2099):
            raise ValueError("年は2024~2099の範囲で入力してください")

        return year

    @field_validator("month")
    def check_month(cls, month):
        if month is not None and not (1 <= month <= 12):
            raise ValueError("月は1~12の範囲で入力してください")
        return month
