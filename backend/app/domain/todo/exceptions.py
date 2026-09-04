from enum import StrEnum


class TodoDomainError(Exception):
    pass


class TodoAlreadyFinished(TodoDomainError):
    pass


class InvalidTodo(TodoDomainError):
    def __init__(self, reason: str):
        self.reason = reason


class TodoValidationReason(StrEnum):
    TITLE_REQUIRED = "TITLE_REQUIRED"
    TITLE_TOO_LONG = "TITLE_TOO_LONG"
    DUE_REQUIRED = "DUE_REQUIRED"
    INVALID_DUE = "INVALID_DUE"
    DETAIL_TOO_LONG = "DETAIL_TOO_LONG"
