from datetime import date
from app.models.time_model import RegisterTargetTimeResponse
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode
from app.repositories.time_repository import TimeRepository
from app.repositories.money_repository import MoneyRepository
from lib.log_conf import logger
from sqlalchemy.exc import IntegrityError


class RegisterTargetTime:
    def __init__(self, db) -> None:
        self.time_repo = TimeRepository(db)
        self.money_repo = MoneyRepository(db)

    def execute(self, activities: list[dict], username: str) -> RegisterTargetTimeResponse:
        results = []
        success_count = 0
        error_count = 0
        for row in activities:
            target_time = row["target_time"]
            date_str = row["date"]
            year, month, day = map(int, date_str.split("-"))
            parsed_date = date(year, month, day)

            # 目標時間を登録する前に、対象月の月収が存在するか確認
            income_month = date(year, month, 1)
            income = self.money_repo.get_monthly_salary(income_month, username)
            if not income:
                results.append(self._build_error_result(
                    parsed_date, NotFoundCode.SALARY_NOT_FOUND
                ))
                error_count += 1
                continue

            try:
                with self.time_repo.begin_nested():
                    self.time_repo.create_activity_with_target_tim(
                        parsed_date, target_time, username)
                    self.time_repo.flush()
                logger.info(f"{username}が複数日の目標時間を登録")
                results.append(self._build_success_result(
                    parsed_date, target_time
                ))
                success_count += 1
            except IntegrityError:
                results.append(self._build_error_result(
                    parsed_date, ConflictCode.TARGET_TIME_ALREADY_REGISTERED
                ))
                error_count += 1
            except Exception as e:
                results.append(self._build_error_result(
                    parsed_date, BadRequestCode.UNEXPECTED_ERROR
                ))
                error_count += 1
                logger.error(
                    f"Error registering target time for {date_str}: {str(e)}", exc_info=True)

        return RegisterTargetTimeResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )

    def _build_error_result(self, parsed_date: date, reason: str) -> dict:
        return {
            "date": self._format_date(parsed_date),
            "reason": reason,
            "result": "error",
            "target_time": None
        }

    def _build_success_result(self, parsed_date: date, target_time: float) -> dict:
        return {
            "date": self._format_date(parsed_date),
            "result": "success",
            "reason": None,
            "target_time": target_time
        }

    def _format_date(self, parsed_date: date) -> str:
        return f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}"
