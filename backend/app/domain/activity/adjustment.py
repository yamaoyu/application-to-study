from dataclasses import dataclass
from app.domain.income.monthly_income import MonthlySalary


@dataclass(frozen=True)
class Adjustment:
    bonus: float
    penalty: float

    @classmethod
    def calculate(
            cls,
            salary: MonthlySalary,
            target_time: float,
            actual_time: float):
        if actual_time >= target_time:
            return cls(
                bonus=salary.amount_for(actual_time),
                penalty=0.0,
            )

        shortage = round(target_time - actual_time, 1)
        return cls(
            bonus=0.0,
            penalty=salary.amount_for(shortage),
        )

    @property
    def pay_adjustment(self) -> float:
        return round(self.bonus - self.penalty, 2)
