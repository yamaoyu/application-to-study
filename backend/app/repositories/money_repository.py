from db import db_model
from sqlalchemy.orm import Session
from sqlalchemy.orm import load_only
from datetime import date


class MoneyRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def insert_monthly_salary(self, income_month: date, salary: float, username: str) -> None:
        data = db_model.Income(income_month=income_month,
                               salary=salary,
                               username=username)
        self.db.add(data)

    def get_monthly_salary(self, income_month: date, username: str) -> db_model.Income:
        return self.db.query(db_model.Income).options(
            load_only(
                db_model.Income.salary,
                db_model.Income.username,
            )
        ).filter(
            db_model.Income.income_month == income_month,
            db_model.Income.username == username).one_or_none()

    def get_yearly_salaries(self, year: int, username: str) -> list[db_model.Income]:
        return self.db.query(db_model.Income).filter(
            db_model.Income.income_month >= date(year, 1, 1),
            db_model.Income.income_month <= date(year, 12, 31),
            db_model.Income.username == username).all()

    def get_all_salaries(self, username: str) -> list[db_model.Income]:
        return self.db.query(db_model.Income).filter(
            db_model.Income.username == username).all()
