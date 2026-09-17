import re
from app.exceptions import DomainValidationError

special_characters = r"[!@#$%&*()+\-=[\]{};:<>,./?_~|]"


class PlainPassword:
    def __init__(self, value: str, field_name: str = "password"):
        if not (8 <= len(value) <= 16):
            raise DomainValidationError(code="INVALID_PASSWORD",
                                        field=field_name,
                                        detail="パスワードは8文字以上、16文字以下としてください")
        if not is_password_complex(value):
            raise DomainValidationError(code="INVALID_PASSWORD",
                                        field=field_name,
                                        detail="パスワードは大文字、小文字、数字、記号をそれぞれ1文字以上含む必要があります")
        self.value = value


def is_password_complex(password: str) -> bool:
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(special_characters, password):
        return False
    return True
