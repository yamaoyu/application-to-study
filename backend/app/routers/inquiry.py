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
from app.dependencies.auth import get_current_user
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden


router = APIRouter(prefix="/inquiries", tags=["inquiries"])


def get_inquiry_service(db):
    return InquiryService(db)


@router.post("", status_code=201, response_model=CreateInquiryResponse)
def send_inquiry(param: CreateInquiryInput,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    service = get_inquiry_service(db)
    return service.create_inquiry(param.category, param.detail)


@router.get("", response_model=GetInquiryResponse)
def get_inquiries(params: InquirySearchQuery = Depends(),
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    service = get_inquiry_service(db)
    return service.get_inquiries(
        params.year,
        params.month,
        params.category,
        params.priority,
        params.is_checked
    )


@router.patch("/{id}", response_model=InquiryItem)
def edit_inquiry(id: int,
                 param: EditInquiryInput,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    service = get_inquiry_service(db)
    return service.edit_inquiry(id, param.priority, param.is_checked)
