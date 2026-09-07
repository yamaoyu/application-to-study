import os
from email_validator import validate_email
from app.exceptions import DomainValidationError

ENV = os.getenv("ENV", "DEV")


class Email:
    def __init__(self, value: str | None):
        if not value:
            self.value = None
            return
        try:
            validate_email(value, check_deliverability=ENV == "PROD")
            self.value = value
        except Exception:
            raise DomainValidationError(
                code="INVALID_EMAIL", field="email", detail="メールアドレスの形式が不正です")
