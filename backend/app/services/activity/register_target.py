from datetime import date
from app.models.time_model import RegisterTargetTimeResponse
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode
from app.repositories.time_repository import TimeRepository
from app.repositories.money_repository import MoneyRepository
from lib.log_conf import logger
from sqlalchemy.exc import IntegrityError
from app.services.activity.utils import format_date, parse_activity_date


class RegisterTargetTimeUseCase:
    def __init__(self, db) -> None:
        self.time_repo = TimeRepository(db)
        self.money_repo = MoneyRepository(db)

    def execute(self, activities: list[dict], username: str) -> RegisterTargetTimeResponse:
        results = []
        success_count = 0
        error_count = 0
        for row in activities:
            target_time = row["target_time"]
            parsed_date = parse_activity_date(row["date"])
            result = self._register_one_target_time(parsed_date, username, target_time)
            results.append(result)

            if result["result"] == "success":
                success_count += 1
            else:
                error_count += 1

        return RegisterTargetTimeResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )

    def _register_one_target_time(self, parsed_date: date, username: str, target_time: float) -> dict:
        try:
            # 目標時間を登録する前に、対象月の月収が存在するか確認
            income_row = self._fetch_monthly_salary(parsed_date, username)
            if not income_row:
                return self._build_error_result(
                    parsed_date, NotFoundCode.SALARY_NOT_FOUND
                )
            with self.time_repo.begin_nested():
                self.time_repo.create_activity_with_target_time(
                    parsed_date, target_time, username)
                self.time_repo.flush()
            logger.info(f"{username}が複数日の目標時間を登録")
            return self._build_success_result(
                parsed_date, target_time
            )
        except IntegrityError:
            return self._build_error_result(
                parsed_date, ConflictCode.TARGET_TIME_ALREADY_REGISTERED
            )
        except Exception as e:
            logger.error(
                f"Error registering target time for {parsed_date}: {str(e)}", exc_info=True)
            return self._build_error_result(
                parsed_date, BadRequestCode.UNEXPECTED_ERROR
            )

    def _build_error_result(self, parsed_date: date, reason: str) -> dict:
        return {
            "date": format_date(parsed_date),
            "reason": reason,
            "result": "error",
            "target_time": None
        }

    def _build_success_result(self, parsed_date: date, target_time: float) -> dict:
        return {
            "date": format_date(parsed_date),
            "result": "success",
            "reason": None,
            "target_time": target_time
        }

    def _fetch_monthly_salary(self, parsed_date: date, username: str):
        income_month = date(parsed_date.year, parsed_date.month, 1)
        return self.money_repo.get_monthly_salary(income_month, username)
