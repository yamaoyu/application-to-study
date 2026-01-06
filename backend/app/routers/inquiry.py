from db.database import get_db
from lib.security import (get_current_user, admin_only, login_required,
                          oauth2_scheme)
from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.models.inquiry_model import (InquiryForm, ResponseInquiry,
                                      Category, Priority, EditInquiry)
from app.services.inquiry_service import InquiryService


router = APIRouter()


def get_inquiry_service(db):
    return InquiryService(db)


@router.post("/inquiries", status_code=201, response_model=ResponseInquiry)
@login_required()
def send_inquiry(param: InquiryForm,
                 db: Session = Depends(get_db),
                 token: str = Depends(oauth2_scheme)):
    service = get_inquiry_service(db)
    return service.create_inquiry(param.category, param.detail)


@router.get("/inquiries")
@admin_only()
def get_inquiries(year: Optional[str] = None,
                  month: Optional[str] = None,
                  category: Optional[Category] = None,
                  priority: Optional[Priority] = None,
                  is_checked: Optional[bool] = None,
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.get_inquiries(year, month, category, priority, is_checked)


@router.put("/inquiries/{id}")
@admin_only()
def edit_inquiry(id: int,
                 param: EditInquiry,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.edit_inquiry(id, param.priority, param.is_checked)
