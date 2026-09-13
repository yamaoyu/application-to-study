from enum import StrEnum


class IncomeDomainError(Exception):
    pass


class IncomeValidationReason(StrEnum):
    INVALID_MONTHLY_INCOME = "INVALID_MONTHLY_INCOME"


class InValidIncome(IncomeDomainError):
    pass
