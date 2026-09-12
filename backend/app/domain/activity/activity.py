import re
from enum import Enum
from dataclasses import dataclass
from app.domain.activity.adjustment import Adjustment
from app.domain.income.monthly_income import MonthlySalary
from app.domain.activity.exceptions import ActivityAlreadyFinished, InvalidActivity


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

    def __init__(self, target_time: float, actual_time: float, status: ActivityStatus, adjustment: Adjustment) -> None:
        if not (0.5 <= target_time <= 12):
            raise InvalidActivity("目標時間は0.5~12.0の範囲で入力してください")

        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", str(target_time)):
            raise InvalidActivity("目標時間は0.5時間単位で入力してください")

        if not (0.0 <= actual_time <= 12):
            raise InvalidActivity("活動時間は0.0~12.0の範囲で入力してください")

        if not re.match(r"^((1[0-2]|\d)\.[0|5])$", str(actual_time)):
            raise InvalidActivity("活動時間は0.5時間単位で入力してください")

        self.target_time = target_time
        self.actual_time = actual_time
        self.status = status
        self.adjustment = adjustment

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

    def effective_adjustment(self, salary: MonthlySalary) -> Adjustment:
        if self.status == ActivityStatus.PENDING:
            return Adjustment.calculate(
                salary=salary,
                target_time=self.target_time,
                actual_time=self.actual_time,
            )

        return self.adjustment
