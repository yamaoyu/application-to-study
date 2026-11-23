from dataclasses import dataclass
from decimal import Decimal

from app.domain.money.constants import ZERO_MONEY


@dataclass(frozen=True)
class ActivityResultSummary:
    success_days: int
    fail_days: int
    pending_days: int
    bonus: Decimal
    penalty: Decimal

    @property
    def pay_adjustment(self) -> Decimal:
        return self.bonus - self.penalty

    @property
    def unsuccessful_days(self) -> int:
        return self.fail_days + self.pending_days

    @classmethod
    def empty(cls) -> "ActivityResultSummary":
        return cls(
            bonus=ZERO_MONEY,
            penalty=ZERO_MONEY,
            success_days=0,
            pending_days=0,
            fail_days=0,
        )
