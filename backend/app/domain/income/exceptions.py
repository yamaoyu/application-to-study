from enum import StrEnum


class IncomeDomainError(Exception):
    pass


class IncomeValidationReason(StrEnum):
    INVALID_MONTHLY_INCOME = "INVALID_MONTHLY_INCOME"


class InValidIncome(IncomeDomainError):
    def __init__(self, reason: IncomeValidationReason, field: str, detail: str):
        self.reason = reason
        self.field = field
        self.detail = detail
