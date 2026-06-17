from dataclasses import dataclass

DIVISOR = 200


@dataclass
class AdjustmentResult:
    bonus: float
    penalty: float


@dataclass
class ActivityResult:
    status: str
    bonus: float
    penalty: float


def calc_adjustment_amount(salary: float, time: float) -> float:
    if time <= 0:
        return 0.0
    return round((salary / DIVISOR) * time, 2)


def calc_time_diff(target_time: float, actual_time: float) -> float:
    return round(target_time - actual_time, 1)


def calc_bonus_penalty(salary: float, target_time: float, actual_time: float) -> AdjustmentResult:
    if actual_time >= target_time:
        return AdjustmentResult(
            bonus=calc_adjustment_amount(salary, actual_time),
            penalty=0.0,
        )

    diff = calc_time_diff(target_time, actual_time)
    return AdjustmentResult(
        bonus=0.0,
        penalty=calc_adjustment_amount(salary, diff),
    )


def calc_activity_result(salary: float, target_time: float, actual_time: float) -> ActivityResult:
    adjustment = calc_bonus_penalty(salary, target_time, actual_time)
    status = "success" if actual_time >= target_time else "failure"
    return ActivityResult(
        status=status,
        bonus=adjustment.bonus,
        penalty=adjustment.penalty,
    )


def round_money(amount: float) -> float:
    return round(amount, 2)
