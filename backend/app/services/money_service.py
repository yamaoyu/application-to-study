from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.money_repository import MoneyRepository
from app.exceptions import NotFound, BadRequest, Conflict
from datetime import date


class MoneyService():
    def __init__(self, db: Session) -> None:
        self.repo = MoneyRepository(db)

    def register_monthly_salary(self, year: int, month: int, salary: float, username: str) -> dict:
        try:
            income_month = date(year, month, 1)
            self.repo.insert_monthly_salary(income_month, salary, username)
            self.repo.flush()
            logger.info(f"{username}:{income_month}の月収を登録")
            return {"message": f"{year}-{month}の月収:{salary}万円"}
        except IntegrityError as sqlalchemy_error:
            if "Duplicate entry" in str(getattr(sqlalchemy_error, "orig", sqlalchemy_error)):
                raise Conflict(detail="その月の月収は既に登録されています")
            raise BadRequest(detail="データの整合性エラーが発生しました。入力データを確認してください")

    def get_monthly_income(self, year: int, month: int, username: str) -> dict:
        income_month = date(year, month, 1)
        result = self.repo.get_monthly_salary(income_month, username)
        if not result:
            raise NotFound(detail=f"{year}-{month}の月収は未登録です")
        total_income = round((result.salary + result.total_bonus - result.total_penalty), 2)
        pay_adjustment = round((result.total_bonus - result.total_penalty), 2)
        logger.info(f"{username}:{year}-{month}の月収を取得")
        return {"month_info": result, "total_income": total_income, "pay_adjustment": pay_adjustment}
