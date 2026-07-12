from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.money_repository import MoneyRepository
from app.repositories.time_repository import TimeRepository
from app.exceptions import NotFound, BadRequest, Conflict
from datetime import date
from lib.common import get_next_month_start
from app.models.money_model import RegisterSalaryResponse, GetIncomeResponse
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode


class MoneyService():
    def __init__(self, db: Session) -> None:
        self.income_repo = MoneyRepository(db)
        self.time_repo = TimeRepository(db)

    def register_monthly_salary(self, year: int, month: int, salary: float, username: str) -> RegisterSalaryResponse:
        try:
            income_month = date(year, month, 1)
            self.income_repo.insert_monthly_salary(income_month, salary, username)
            self.income_repo.flush()
            logger.info(f"{username}:{income_month}の月収を登録")
            return RegisterSalaryResponse(year=year, month=month, salary=salary)
        except IntegrityError as sqlalchemy_error:
            if "Duplicate entry" in str(getattr(sqlalchemy_error, "orig", sqlalchemy_error)):
                raise Conflict(code=ConflictCode.SALARY_ALREADY_EXISTS)
            raise BadRequest(code=BadRequestCode.UNEXPECTED_ERROR)

    def get_monthly_income(self, year: int, month: int, username: str) -> GetIncomeResponse:
        income_month = date(year, month, 1)
        income = self.income_repo.get_monthly_salary(income_month, username)
        if not income:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND)
        end_date = get_next_month_start(income_month)
        activity_summary = self.time_repo.get_activity_summary(
            username, income_month, end_date)
        total_bonus = round(activity_summary["bonus"], 2)
        total_penalty = round(activity_summary["penalty"], 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)
        logger.info(f"{username}:{year}-{month}の月収を取得")
        return GetIncomeResponse(
            base_income=income.salary,
            pay_adjustment=pay_adjustment,
            total_bonus=total_bonus,
            total_penalty=total_penalty
        )
