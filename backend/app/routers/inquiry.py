from db.database import get_db
from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.models.inquiry_model import (InquiryForm, ResponseCreateInquiry,
                                      Category, Priority, EditInquiry,
                                      InquiryResponse)
from app.services.inquiry_service import InquiryService
from app.dependencies.auth import get_current_user, admin_only


router = APIRouter()


def get_inquiry_service(db):
    return InquiryService(db)


@router.post("/inquiries", status_code=201, response_model=ResponseCreateInquiry)
def send_inquiry(param: InquiryForm,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.create_inquiry(param.category, param.detail)


@router.get("/inquiries", response_model=list[InquiryResponse])
@admin_only()
def get_inquiries(year: Optional[int] = None,
                  month: Optional[int] = None,
                  category: Optional[Category] = None,
                  priority: Optional[Priority] = None,
                  is_checked: Optional[bool] = None,
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.get_inquiries(year, month, category, priority, is_checked)


@router.put("/inquiries/{id}", response_model=InquiryResponse)
@admin_only()
def edit_inquiry(id: int,
                 param: EditInquiry,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.edit_inquiry(id, param.priority, param.is_checked)
