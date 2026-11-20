from dataclasses import dataclass
from decimal import Decimal

from app.domain.income.monthly_income import MonthlySalary


@dataclass(frozen=True)
class Adjustment:
    bonus: Decimal
    penalty: Decimal

    @classmethod
    def calculate(cls, salary: MonthlySalary, target_time: float, actual_time: float):
        if actual_time >= target_time:
            return cls(
                bonus=salary.amount_for(actual_time),
                penalty=Decimal("0.0"),
            )

        shortage = _calc_shortage(target_time, actual_time)
        return cls(
            bonus=Decimal("0.0"),
            penalty=salary.amount_for(shortage),
        )

    @property
    def pay_adjustment(self) -> Decimal:
        return round(self.bonus - self.penalty, 2)


def _calc_shortage(target_time: float, actual_time: float) -> float:
    return round(target_time - actual_time, 1)
