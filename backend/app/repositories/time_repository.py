from db import db_model
from sqlalchemy.orm import Session


class TimeRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def rollback(self) -> None:
        self.db.rollback()

    def begin_nested(self) -> None:
        return self.db.begin_nested()

    def get_activity_by_date_and_username(self, date: str, username: str) -> db_model.Activity:
        return self.db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == username).one_or_none()

    def get_monthly_activities(self, start_date, end_date, username: str) -> list[db_model.Activity]:
        return self.db.query(db_model.Activity).filter(
            db_model.Activity.date.between(start_date, end_date),
            db_model.Activity.username == username).order_by(
            db_model.Activity.date).all()

    def get_yearly_activities(self, start_date, end_date, username: str) -> list[db_model.Activity]:
        return self.db.query(db_model.Activity).filter(
            db_model.Activity.date.between(start_date, end_date),
            db_model.Activity.username == username).order_by(
                db_model.Activity.date).all()

    def get_all_activities(self, username: str, status: bool = None) -> list[db_model.Activity]:
        sqlstatement = self.db.query(db_model.Activity).filter(
            db_model.Activity.username == username)
        if status is not None:
            sqlstatement = sqlstatement.filter(db_model.Activity.status == status)
        return sqlstatement.order_by(db_model.Activity.date).all()

    def insert_target_time(self, date: str, target_time: int, username: str) -> None:
        insert_data = db_model.Activity(
            date=date, target_time=target_time, username=username)
        self.db.add(insert_data)

    def update_actual_time(self, activity: db_model.Activity, actual_time: int) -> None:
        activity.actual_time = actual_time

    def update_activity_status_and_bonus(self, activity: db_model.Activity, status: str, bonus: float, penalty: float) -> None:
        activity.status = status
        activity.bonus = bonus
        activity.penalty = penalty
