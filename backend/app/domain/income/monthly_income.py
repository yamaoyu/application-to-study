from dataclasses import dataclass


@dataclass(frozen=True)
class MonthlySalary:
    salary: float

    def amount_for(self, time: float) -> float:
        return round((self.salary / 200) * time, 2)
