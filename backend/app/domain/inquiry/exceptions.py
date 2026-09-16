from enum import StrEnum


class InquiryDomainError(Exception):
    pass


class InquiryValidationReason(StrEnum):
    INQUIRY_DETAIL_TOO_LONG = "INQUIRY_DETAIL_TOO_LONG"
    INQUIRY_DETAIL_REQUIRED = "INQUIRY_DETAIL_REQUIRED"


class InValidInquiry(InquiryDomainError):
    def __init__(self, reason: InquiryValidationReason, field: str, detail: str):
        self.reason = reason
        self.field = field
        self.detail = detail
