from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ActivityResultSummary:
    success_days: int
    fail_days: int
    pending_days: int
    bonus: Decimal
    penalty: Decimal

    @property
    def total_bonus(self) -> Decimal:
        return self.bonus

    @property
    def total_penalty(self) -> Decimal:
        return self.penalty

    @property
    def pay_adjustment(self) -> Decimal:
        return self.total_bonus - self.total_penalty

    @property
    def unsuccessful_days(self) -> int:
        return self.fail_days + self.pending_days

    @classmethod
    def empty(cls) -> "ActivityResultSummary":
        return cls(
            bonus=Decimal("0.0"),
            penalty=Decimal("0.0"),
            success_days=0,
            pending_days=0,
            fail_days=0,
        )
