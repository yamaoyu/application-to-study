from datetime import date
from app.models.time_model import FinishActivityResponse
from app.domain.activity.activity import Activity, ActivityStatus, Adjustment
from app.domain.income.monthly_income import MonthlySalary
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode
from app.repositories.time_repository import TimeRepository
from app.repositories.money_repository import MoneyRepository
from app.domain.activity.exceptions import ActivityAlreadyFinished
from lib.log_conf import logger


class FinishActivities:
    def __init__(self, db) -> None:
        self.time_repo = TimeRepository(db)
        self.money_repo = MoneyRepository(db)

    def execute(self, dates: list[str], username: str) -> FinishActivityResponse:
        bonus_sum = 0
        penalty_sum = 0
        results = []
        success_count = 0
        error_count = 0

        for date_str in dates:
            year, month, day = map(int, date_str.split("-"))
            parsed_date = date(year, month, day)
            income_month = date(year, month, 1)
            income = self.money_repo.get_monthly_salary(income_month, username)
            if not income:
                error_count += 1
                results.append(self._build_error_result(
                    parsed_date, NotFoundCode.SALARY_NOT_FOUND
                ))
                continue
            monthly_income = MonthlySalary(income.salary)

            activity_row = self.time_repo.get_activity_by_date_and_username(
                parsed_date, username)
            if not activity_row:
                error_count += 1
                results.append(self._build_error_result(
                    parsed_date, NotFoundCode.ACTIVITY_NOT_FOUND))
                continue

            try:
                activity = Activity(
                    target_time=activity_row.target_time,
                    actual_time=activity_row.actual_time,
                    status=ActivityStatus(activity_row.status),
                    adjustment=Adjustment(0, 0)
                )
                activity.finish(monthly_income)
                with self.time_repo.begin_nested():
                    self.time_repo.update_activity_status_and_bonus(
                        activity_row, activity.status.value, activity.adjustment.bonus, activity.adjustment.penalty)
                    self.time_repo.flush()
                results.append(self._build_success_result(parsed_date, activity))
                bonus_sum += activity.adjustment.bonus
                penalty_sum += activity.adjustment.penalty
                success_count += 1
            except ActivityAlreadyFinished:
                error_count += 1
                results.append(self._build_error_result(
                    parsed_date,
                    ConflictCode.ACTIVITY_ALREADY_FINISHED
                ))
            except Exception as e:
                logger.error(f"Error finishing activity for {date_str}: {str(e)}")
                error_count += 1
                results.append(self._build_error_result(
                    parsed_date,
                    BadRequestCode.UNEXPECTED_ERROR
                ))

        round_bonus = round(bonus_sum, 2)
        round_penalty = round(penalty_sum, 2)
        pay_adjustment = round(round_bonus - round_penalty, 2)
        return FinishActivityResponse(
            success_count=success_count,
            error_count=error_count,
            pay_adjustment=pay_adjustment,
            total_bonus=round_bonus,
            total_penalty=round_penalty,
            results=results
        )

    def _build_error_result(self, parsed_date: date, reason: str) -> dict:
        return {
            "date": self._format_date(parsed_date),
            "reason": reason,
            "result": "error",
            "bonus": None,
            "penalty": None,
            "status": None,
        }

    def _build_success_result(self, parsed_date: date, activity: Activity) -> dict:
        return {
            "date": self._format_date(parsed_date),
            "status": activity.status.value,
            "bonus": activity.adjustment.bonus,
            "penalty": activity.adjustment.penalty,
            "result": "success",
            "reason": None,
        }

    def _format_date(self, parsed_date: date) -> str:
        return f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}"
