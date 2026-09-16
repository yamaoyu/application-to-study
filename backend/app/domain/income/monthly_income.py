from dataclasses import dataclass
from app.domain.income.exceptions import InValidIncome, IncomeValidationReason


@dataclass()
class MonthlySalary:
    salary: float

    def __init__(self, salary: float) -> None:
        if not (5 <= salary <= 2000):
            raise InValidIncome(reason=IncomeValidationReason.INVALID_MONTHLY_INCOME,
                                field="salary", detail="月収は5以上2000以下としてください")

        self.salary = salary

    def amount_for(self, time: float) -> float:
        return round((self.salary / 200) * time, 2)
