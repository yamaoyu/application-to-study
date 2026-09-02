from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.money_repository import MoneyRepository
from app.repositories.activity_repository import ActivityRepository
from app.exceptions import BadRequest, Conflict
from datetime import date
from app.models.money_model import RegisterSalaryResponse
from app.error_codes import ConflictCode, BadRequestCode


class RegisterSalaryUsecase():
    def __init__(self, db: Session) -> None:
        self.income_repo = MoneyRepository(db)
        self.time_repo = ActivityRepository(db)

    def execute(self, year: int, month: int, salary: float, username: str) -> RegisterSalaryResponse:
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
