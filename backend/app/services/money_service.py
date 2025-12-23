from app.models.common_model import CheckDate
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.repositories.money_repository import MoneyRepository
from app.exceptions import NotFound, BadRequest, Conflict


class MoneyService():
    def __init__(self, db: Session) -> None:
        self.repo = MoneyRepository(db)

    def register_monthly_salary(self, year: int, month: int, salary: float, username: str) -> dict:
        try:
            CheckDate(year=year, month=month)
        except ValidationError as validate_e:
            raise BadRequest(detail=str(validate_e.errors()[0]["ctx"]["error"]))
        try:
            salary = salary
            year_month = f"{year}-{month}"
            self.repo.insert_monthly_salary(year_month, salary, username)
            self.repo.flush()
            logger.info(f"{username}:{year_month}の月収を登録")
            return {"message": f"{year_month}の月収:{salary}万円"}
        except IntegrityError as sqlalchemy_error:
            if "Duplicate entry" in str(getattr(sqlalchemy_error, "orig", sqlalchemy_error)):
                raise Conflict(detail="その月の月収は既に登録されています")
            raise BadRequest(detail="データの整合性エラーが発生しました。入力データを確認してください")

    def get_monthly_income(self, year: int, month: int, username: str) -> dict:
        try:
            CheckDate(year=year, month=month)
        except ValidationError as validate_e:
            raise BadRequest(detail=str(validate_e.errors()[0]["ctx"]["error"]))
        year_month = f"{year}-{month}"
        result = self.repo.get_monthly_salary(year_month, username)
        if not result:
            raise NotFound(detail=f"{year_month}の月収は未登録です")
        total_income = round((result.salary + result.total_bonus - result.total_penalty), 2)
        pay_adjustment = round((result.total_bonus - result.total_penalty), 2)
        logger.info(f"{username}:{year_month}の月収を取得")
        return {"month_info": result, "total_income": total_income, "pay_adjustment": pay_adjustment}
