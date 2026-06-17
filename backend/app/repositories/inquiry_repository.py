from datetime import datetime, date
from db import db_model
from sqlalchemy.orm import Session
from app.models.inquiry_model import Category, Priority
from typing import Optional


class InquiryRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def insert_inquiry(self, category: str, detail: str, inquiry_date: date) -> None:
        insert_data = db_model.Inquiry(category=category,
                                       detail=detail,
                                       date=inquiry_date)
        self.db.add(insert_data)

    def update_date(self, inquiry: db_model.Inquiry, inquiry_date: date) -> None:
        inquiry.date = inquiry_date

    def update_priority(self, inquiry: db_model.Inquiry, priority: Priority) -> None:
        inquiry.priority = priority

    def update_is_checked(self, inquiry: db_model.Inquiry, is_checked: bool) -> None:
        inquiry.is_checked = is_checked

    def get_inquiry_by_id(self, id: int) -> Optional[db_model.Inquiry]:
        return self.db.query(db_model.Inquiry).filter(
            db_model.Inquiry.id == id).one_or_none()

    def get_inquiry_by_content(self, category: str, detail: str) -> Optional[db_model.Inquiry]:
        return self.db.query(db_model.Inquiry).filter(
            db_model.Inquiry.category == category,
            db_model.Inquiry.detail == detail).one_or_none()

    def get_inquiries(self,
                      year: Optional[int],
                      month: Optional[int],
                      category: Optional[Category],
                      priority: Optional[Priority],
                      is_checked: Optional[bool]) -> list[db_model.Inquiry]:
        # インプットに応じてsql文を作成
        sqlstatement = self.db.query(db_model.Inquiry)
        if year and month:
            start_date = datetime(int(year), int(month), 1).date()
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date()
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date()
            sqlstatement = sqlstatement.filter(
                db_model.Inquiry.date.between(start_date, end_date))
        if category:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.category == category)
        if priority:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.priority == priority)
        if is_checked is not None:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.is_checked == is_checked)
        return sqlstatement.all()
