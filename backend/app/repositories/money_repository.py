from db import db_model
from sqlalchemy.orm import Session


class MoneyRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def insert_monthly_salary(self, year_month: str, salary: float, username: str) -> None:
        data = db_model.Income(year_month=year_month,
                               salary=salary,
                               username=username)
        self.db.add(data)

    def get_monthly_salary(self, year_month: str, username: str) -> db_model.Income:
        return self.db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == username).one_or_none()

    def get_yearly_salaries(self, year: int, username: str) -> list[db_model.Income]:
        return self.db.query(db_model.Income).filter(
            db_model.Income.year_month.like(f"{year}%"),
            db_model.Income.username == username).all()

    def get_all_salaries(self, username: str) -> list[db_model.Income]:
        return self.db.query(db_model.Income).filter(
            db_model.Income.username == username).all()

    def update_bonus_and_penalty(self, income: db_model.Income, total_bonus: float, total_penalty: float) -> None:
        income.total_bonus = total_bonus
        income.total_penalty = total_penalty
