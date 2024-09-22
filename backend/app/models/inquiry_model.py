from enum import Enum
from pydantic import BaseModel
from typing import Optional


class Category(str, Enum):
    request = "要望"
    error = "エラー報告"
    other = "その他"


class Priority(str, Enum):
    high = "高"
    middle = "中"
    low = "低"


class InquiryForm(BaseModel):
    category: Category
    detail: str


class ResponseInquiry(InquiryForm):
    message: str


class GetInquiry(BaseModel):
    year: Optional[str] = None
    month: Optional[str] = None
    day: Optional[str] = None
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None


class EditInquiry(BaseModel):
    priority: Optional[Priority] = None
    is_checked: Optional[bool] = None
