from enum import Enum
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import date


class Category(str, Enum):
    request = "要望"
    error = "エラー報告"
    other = "その他"


class Priority(str, Enum):
    high = "高"
    middle = "中"
    low = "低"


class InquiryForm(BaseModel):
    category: str
    detail: str

    @field_validator("category")
    def validate_target_time(cls, category):
        if category not in Category:
            raise ValueError("カテゴリは要望・エラー報告・その他から選択してください")
        return category

    @field_validator("detail")
    def check_detail_length(cls, detail):
        if len(detail) > 256:
            raise ValueError("詳細は256文字以内で入力してください")
        return detail


class ResponseCreateInquiry(InquiryForm):
    pass


class InquiryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    detail: str
    date: date
    category: Category
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None


class EditInquiry(BaseModel):
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None
