from dataclasses import dataclass
from app.domain.money.amount import round_money_amount


@dataclass(frozen=True)
class ActivityResultSummary:
    success_days: int
    fail_days: int
    pending_days: int
    bonus: float
    penalty: float

    @property
    def total_bonus(self) -> float:
        return round_money_amount(self.bonus)

    @property
    def total_penalty(self) -> float:
        return round_money_amount(self.penalty)

    @property
    def pay_adjustment(self) -> float:
        return round_money_amount(self.total_bonus - self.total_penalty)

    @property
    def unsuccessful_days(self) -> int:
        return self.fail_days + self.pending_days

    @classmethod
    def empty(cls) -> "ActivityResultSummary":
        return cls(
            bonus=0.0,
            penalty=0.0,
            success_days=0,
            pending_days=0,
            fail_days=0,
        )
