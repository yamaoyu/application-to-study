from enum import StrEnum


class InquiryDomainError(Exception):
    pass


class InquiryValidationReason(StrEnum):
    INQUIRY_DETAIL_TOO_LONG = "INQUIRY_DETAIL_TOO_LONG"
    INQUIRY_DETAIL_REQUIRED = "INQUIRY_DETAIL_REQUIRED"


class InValidInquiry(InquiryDomainError):
    pass
