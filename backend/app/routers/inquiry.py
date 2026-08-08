from db.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.inquiry_model import (CreateInquiryInput,
                                      CreateInquiryResponse,
                                      InquirySearchQuery,
                                      EditInquiryInput,
                                      GetInquiryResponse,
                                      InquiryItem)
from app.services.inquiry_service import InquiryService
from app.dependencies.auth import get_current_user, admin_only


router = APIRouter()


def get_inquiry_service(db):
    return InquiryService(db)


@router.post("/inquiries", status_code=201, response_model=CreateInquiryResponse)
def send_inquiry(param: CreateInquiryInput,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.create_inquiry(param.category, param.detail)


@router.get("/inquiries", response_model=GetInquiryResponse)
@admin_only()
def get_inquiries(params: InquirySearchQuery = Depends(),
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.get_inquiries(
        params.year,
        params.month,
        params.category,
        params.priority,
        params.is_checked
    )


@router.put("/inquiries/{id}", response_model=InquiryItem)
@admin_only()
def edit_inquiry(id: int,
                 param: EditInquiryInput,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.edit_inquiry(id, param.priority, param.is_checked)
