from enum import Enum
from dataclasses import dataclass
from app.domain.activity.adjustment import Adjustment
from app.domain.income.monthly_income import MonthlySalary
from app.domain.activity.exceptions import ActivityAlreadyFinished


class ActivityStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"

    def is_finished(self) -> bool:
        return self in {self.SUCCESS, self.FAILURE}


@dataclass
class Activity:
    target_time: float
    actual_time: float
    status: ActivityStatus
    adjustment: Adjustment

    def _judge_status(self) -> ActivityStatus:
        if self.target_time > self.actual_time:
            return ActivityStatus.FAILURE
        return ActivityStatus.SUCCESS

    def finish(self, salary: MonthlySalary) -> None:
        if self.status.is_finished():
            raise ActivityAlreadyFinished()

        self.status = self._judge_status()
        self.adjustment = Adjustment.calculate(
            salary=salary,
            target_time=self.target_time,
            actual_time=self.actual_time)
