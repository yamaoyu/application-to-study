from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.repositories.money_repository import MoneyRepository
from app.repositories.activity_repository import ActivityRepository
from app.exceptions import NotFound
from datetime import date
from lib.common import get_month_end
from app.models.money_model import GetIncomeResponse
from app.error_codes import NotFoundCode


class GetMonthlyIncomeUsecase():
    def __init__(self, db: Session) -> None:
        self.income_repo = MoneyRepository(db)
        self.time_repo = ActivityRepository(db)

    def execute(self, year: int, month: int, username: str) -> GetIncomeResponse:
        income_month = date(year, month, 1)
        income = self.income_repo.get_monthly_salary(income_month, username)
        if not income:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND)
        end_date = get_month_end(income_month)
        activity_summary = self.time_repo.get_activity_summary(
            username, income_month, end_date)
        logger.info(f"{username}:{year}-{month}の月収を取得")
        return GetIncomeResponse(
            base_income=income.salary,
            pay_adjustment=activity_summary.pay_adjustment,
            total_bonus=activity_summary.total_bonus,
            total_penalty=activity_summary.total_penalty
        )
