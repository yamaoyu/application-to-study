from dataclasses import dataclass
from app.domain.income.exceptions import InValidIncome


@dataclass()
class MonthlySalary:
    salary: float

    def __init__(self, salary: float) -> None:
        if salary < 5:
            raise InValidIncome()
        elif salary > 2000:
            raise InValidIncome()

        self.salary = salary

    def amount_for(self, time: float) -> float:
        return round((self.salary / 200) * time, 2)
