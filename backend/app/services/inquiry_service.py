from lib.log_conf import logger
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.inquiry_repository import InquiryRepository
from app.exceptions import NotFound, BadRequest
from app.models.common_model import CheckYearMonth
from typing import Optional


class InquiryService():
    def __init__(self, db: Session) -> None:
        self.repo = InquiryRepository(db)

    def create_inquiry(self, category: str, detail: str) -> dict:
        date = datetime.today()
        inquiry = self.repo.get_inquiry_by_content(category, detail, date)
        # 同じ内容で登録があれば日付を更新
        if inquiry:
            self.repo.update_date(inquiry, date)
        # 同じ内容で登録がなければ追加
        else:
            self.repo.insert_inquiry(category, detail, date)
        logger.info("問い合わせを受付")
        return {
            "category": category,
            "detail": detail,
            "message": "こちらの内容で受け付けました"
        }

    def get_inquiries(self, year: int, month: int, category: str, priority: str, is_checked: bool) -> dict:
        if not year and month:
            raise BadRequest(detail="月を指定する場合は年も指定してください")
        if year and month:
            CheckYearMonth(year, month)
        inquiries = self.repo.get_inquiries(year, month, category, priority, is_checked)
        if not inquiries:
            message = ""
            if year and month:
                message += f"期間が「{year}-{month}」、"
            if category:
                message += f"カテゴリが「{category}」、"
            if priority:
                message += f"優先度が「{priority}」、"
            if is_checked is not None:
                message += f"確認済みが「{is_checked}」、"
            if message:
                message = message[:-1] + "の"
            raise NotFound(detail=f"{message}問い合わせはありません")
        return inquiries

    def edit_inquiry(self, id: int, priority: Optional[str], is_checked: Optional[bool]) -> dict:
        inquiry = self.repo.get_inquiry_by_id(id)
        if not inquiry:
            raise NotFound(detail=f"idが「{id}の問い合わせはありません」")
        if priority is not None:
            self.repo.update_priority(inquiry, priority)
        if is_checked is not None:
            self.repo.update_is_checked(inquiry, is_checked)
        return inquiry
