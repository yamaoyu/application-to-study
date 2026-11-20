from dataclasses import dataclass
from decimal import Decimal

from app.domain.income.exceptions import IncomeValidationReason, InValidIncome


@dataclass()
class MonthlySalary:
    salary: Decimal

    def __init__(self, salary: Decimal) -> None:
        if not (5 <= salary <= 2000):
            raise InValidIncome(
                reason=IncomeValidationReason.INVALID_MONTHLY_INCOME,
                field="salary",
                detail="月収は5以上2000以下としてください",
            )

        self.salary = salary

    def amount_for(self, time: float) -> Decimal:
        # 0.5刻みのtimeに誤差が出ないように文字列にしてから変換する
        return round((self.salary / 200) * Decimal(str(time)), 2)
