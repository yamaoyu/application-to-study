from lib.log_conf import logger
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.inquiry_repository import InquiryRepository
from app.exceptions import NotFound, DomainValidationError
from typing import Optional
from app.models.inquiry_model import Category, Priority, GetInquiryResponse, InquiryItem
from db import db_model
from app.error_codes import NotFoundCode, ValidationErrorCode
from app.domain.inquiry.exceptions import InValidInquiry, InquiryValidationReason
from app.domain.inquiry.inquiry import InquiryDetail


INQUIRY_VALIDATION_REASON_TO_ERROR_CODE = {
    InquiryValidationReason.INQUIRY_DETAIL_TOO_LONG: ValidationErrorCode.INQUIRY_DETAIL_TOO_LONG,
    InquiryValidationReason.INQUIRY_DETAIL_REQUIRED: ValidationErrorCode.INQUIRY_DETAIL_REQUIRED
}


def to_inquiry_bad_request_code(reason: InquiryValidationReason) -> ValidationErrorCode:
    return INQUIRY_VALIDATION_REASON_TO_ERROR_CODE[reason]


class InquiryService():
    def __init__(self, db: Session) -> None:
        self.repo = InquiryRepository(db)

    def create_inquiry(self, category: str, detail: str) -> dict:
        # 詳細を検証
        try:
            inquiry_detail = InquiryDetail(value=detail)
        except InValidInquiry as e:
            raise DomainValidationError(
                code=to_inquiry_bad_request_code(e.reason), field=e.field, detail=e.detail)

        today = date.today()
        inquiry = self.repo.get_inquiry_by_content(category, inquiry_detail.value)
        # 同じ内容で登録があれば日付を更新
        if inquiry:
            self.repo.update_date(inquiry, today)
        # 同じ内容で登録がなければ追加
        else:
            self.repo.insert_inquiry(category, inquiry_detail.value, today)
        logger.info("問い合わせを受付")
        return {
            "category": category,
            "detail": inquiry_detail.value
        }

    def get_inquiries(self,
                      year: Optional[int],
                      month: Optional[int],
                      category: Optional[Category],
                      priority: Optional[Priority],
                      is_checked: Optional[bool]) -> GetInquiryResponse:
        inquiries = self.repo.get_inquiries(year, month, category, priority, is_checked)
        if not inquiries:
            message = ""
            if year and month:
                message += f"期間が「{year}-{month}」、"
            if category:
                message += f"カテゴリが「{category.value}」、"
            if priority:
                message += f"優先度が「{priority.value}」、"
            if is_checked is not None:
                message += f"確認済みが「{is_checked}」、"
            if message:
                message = message[:-1] + "の"
            return GetInquiryResponse(inquiries=[])
        # SQLAlchemyモデルから整形してpydanticで列名を確認できるようにする
        converted_inquiries = [InquiryItem.model_validate(inquiry) for inquiry in inquiries]
        return GetInquiryResponse(inquiries=converted_inquiries)

    def edit_inquiry(self, id: int, priority: Optional[Priority], is_checked: Optional[bool]) -> db_model.Inquiry:
        inquiry = self.repo.get_inquiry_by_id(id)
        if not inquiry:
            raise NotFound(code=NotFoundCode.INQUIRY_NOT_FOUND)
        if priority is not None:
            self.repo.update_priority(inquiry, priority)
        if is_checked is not None:
            self.repo.update_is_checked(inquiry, is_checked)
        return inquiry
