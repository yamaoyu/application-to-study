from datetime import date
from app.models.activity_model import RegisterActualTimeResponse
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode
from app.repositories.activity_repository import ActivityRepository
from app.repositories.money_repository import MoneyRepository
from lib.log_conf import logger
from app.services.activity.utils import format_date, parse_activity_date


class RegisterActualTimeUseCase:
    def __init__(self, db) -> None:
        self.time_repo = ActivityRepository(db)
        self.money_repo = MoneyRepository(db)

    def execute(self,
                activities: list[dict],
                username: str
                ) -> RegisterActualTimeResponse:
        results = []
        success_count = 0
        error_count = 0
        for row in activities:
            actual_time = row["actual_time"]
            parsed_date = parse_activity_date(row["date"])
            result = self._update_one_actual_time(parsed_date, username, actual_time)
            results.append(result)

            if result["result"] == "success":
                success_count += 1
            else:
                error_count += 1

        return RegisterActualTimeResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )

    def _build_error_result(self, parsed_date: date, reason: str) -> dict:
        return {
            "date": format_date(parsed_date),
            "reason": reason,
            "result": "error",
            "actual_time": None
        }

    def _update_one_actual_time(self, parsed_date: date, username: str, actual_time: float) -> dict:
        # 活動時間を登録する前に、その日の活動実績が存在するか確認
        income_row = self._fetch_monthly_salary(parsed_date, username)
        if not income_row:
            return self._build_error_result(
                parsed_date, NotFoundCode.SALARY_NOT_FOUND
            )

        activity_row = self.time_repo.get_activity_by_date_and_username(
            parsed_date, username)
        if not activity_row:
            return self._build_error_result(
                parsed_date, NotFoundCode.ACTIVITY_NOT_FOUND
            )
        # ドメイン層で行う内容が増えるのであればここはドメイン層に移す
        if activity_row.status != "pending":
            return self._build_error_result(
                parsed_date, ConflictCode.ACTIVITY_ALREADY_FINISHED
            )

        try:
            with self.time_repo.begin_nested():
                self.time_repo.update_actual_time(activity_row, actual_time)
                self.time_repo.flush()
            logger.info(f"{username}が複数日の実績時間を登録")
            return self._build_success_result(
                parsed_date, actual_time
            )
        except Exception as e:
            logger.error(
                f"Error registering actual time for {parsed_date}: {str(e)}", exc_info=True)

            return self._build_error_result(
                parsed_date, BadRequestCode.UNEXPECTED_ERROR
            )

    def _build_success_result(self, parsed_date: date, actual_time: float) -> dict:
        return {
            "date": format_date(parsed_date),
            "result": "success",
            "reason": None,
            "actual_time": actual_time
        }

    def _fetch_monthly_salary(self, parsed_date: date, username: str):
        income_month = date(parsed_date.year, parsed_date.month, 1)
        return self.money_repo.get_monthly_salary(income_month, username)
