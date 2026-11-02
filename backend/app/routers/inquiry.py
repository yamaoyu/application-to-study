from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden
from app.models.inquiry_model import (
    CreateInquiryInput,
    CreateInquiryResponse,
    EditInquiryInput,
    GetInquiryResponse,
    InquiryItem,
    InquirySearchQuery,
)
from app.services.inquiry.inquiry_service import InquiryService
from db.database import get_db

router = APIRouter(prefix="/inquiries", tags=["inquiries"])


def get_inquiry_service(db):
    return InquiryService(db)


@router.post("", status_code=201, response_model=CreateInquiryResponse)
def send_inquiry(
    param: CreateInquiryInput,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    service = get_inquiry_service(db)
    return service.create_inquiry(param.category, param.detail)


@router.get("", response_model=GetInquiryResponse)
def get_inquiries(
    params: Annotated[InquirySearchQuery, Depends()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    service = get_inquiry_service(db)
    return service.get_inquiries(
        params.year, params.month, params.category, params.priority, params.is_checked
    )


@router.patch("/{id}", response_model=InquiryItem)
def edit_inquiry(
    id: int,
    param: EditInquiryInput,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    if current_user["role"] != "admin":
        raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
    service = get_inquiry_service(db)
    return service.edit_inquiry(id, param.priority, param.is_checked)
