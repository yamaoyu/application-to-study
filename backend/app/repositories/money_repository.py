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
