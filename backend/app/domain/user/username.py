from app.exceptions import DomainValidationError


class Username:
    def __init__(self, value: str):
        if not (3 <= len(value) <= 16):
            raise DomainValidationError(code="INVALID_USERNAME",
                                        field="username",
                                        detail="ユーザー名は3文字以上、16文字以下としてください")
        self.value = value
