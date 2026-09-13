from dataclasses import dataclass
from app.domain.inquiry.exceptions import InValidInquiry, InquiryValidationReason


@dataclass(frozen=True)
class InquiryDetail:
    value: str

    def __post_init__(self):
        normalized = self.value.strip()

        if not normalized:
            raise InValidInquiry(InquiryValidationReason.INQUIRY_DETAIL_REQUIRED, "詳細は必須です")

        if len(normalized) > 256:
            raise InValidInquiry(InquiryValidationReason.INQUIRY_DETAIL_TOO_LONG,
                                 "詳細は256文字以内で入力してください")

        # "  hello  "が"hello"として扱われるように、正規化された値を設定する
        object.__setattr__(self, "value", normalized)
