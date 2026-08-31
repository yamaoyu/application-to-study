from db import db_model
from datetime import date
from sqlalchemy.orm import Session, SessionTransaction
from sqlalchemy import func, case, extract
from typing import Optional
from app.domain.money.amount import round_money_amount


class ActivityRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def rollback(self) -> None:
        self.db.rollback()

    def begin_nested(self) -> SessionTransaction:
        return self.db.begin_nested()

    def get_activity_by_date_and_username(self, day: date, username: str) -> Optional[db_model.Activity]:
        return self.db.query(db_model.Activity).filter(
            db_model.Activity.date == day,
            db_model.Activity.username == username).one_or_none()

    def get_monthly_activities(self, start_date: date, end_date: date, username: str) -> list[db_model.Activity]:
        return self.db.query(db_model.Activity).filter(
            db_model.Activity.date >= start_date,
            db_model.Activity.date <= end_date,
            db_model.Activity.username == username).order_by(
            db_model.Activity.date).all()

    def get_yearly_activities(self, start_date: date, end_date: date, username: str) -> list[db_model.Activity]:
        return self.db.query(db_model.Activity).filter(
            db_model.Activity.date >= start_date,
            db_model.Activity.date <= end_date,
            db_model.Activity.username == username).order_by(
                db_model.Activity.date).all()

    def count_all_activities(self, username: str, status: Optional[str] = None) -> int:
        sqlstatement = self.db.query(db_model.Activity).filter(
            db_model.Activity.username == username)
        if status is not None:
            sqlstatement = sqlstatement.filter(db_model.Activity.status == status)
        return sqlstatement.order_by(db_model.Activity.date).count()

    def get_all_activities(self, username: str, status: Optional[str] = None) -> list[db_model.Activity]:
        sqlstatement = self.db.query(db_model.Activity).filter(
            db_model.Activity.username == username)
        if status is not None:
            sqlstatement = sqlstatement.filter(db_model.Activity.status == status)
        return sqlstatement.order_by(db_model.Activity.date).all()

    def create_activity_with_target_time(self, target_date: date, target_time: float, username: str) -> None:
        insert_data = db_model.Activity(
            date=target_date, target_time=target_time, username=username)
        self.db.add(insert_data)

    def update_actual_time(self, activity: db_model.Activity, actual_time: float) -> None:
        activity.actual_time = actual_time

    def update_activity_status_and_bonus(self, activity: db_model.Activity, status: str, bonus: float, penalty: float) -> None:
        activity.status = status
        activity.bonus = bonus
        activity.penalty = penalty

    def get_activity_summary(self, username: str, start_date: date | None = None, end_date: date | None = None) -> dict:
        query = self.db.query(
            func.coalesce(func.sum(db_model.Activity.bonus), 0.0).label("bonus"),
            func.coalesce(func.sum(db_model.Activity.penalty), 0.0).label("penalty"),
            func.sum(case((db_model.Activity.status == "success", 1), else_=0)
                     ).label("success_days"),
            func.sum(case((db_model.Activity.status == "pending", 1), else_=0)
                     ).label("pending_days"),
            func.sum(case((db_model.Activity.status == "failure", 1), else_=0)).label("fail_days"),
        ).filter(
            db_model.Activity.username == username,
        )
        if start_date is not None:
            query = query.filter(db_model.Activity.date >= start_date)
        if end_date is not None:
            query = query.filter(db_model.Activity.date <= end_date)
        result = query.one()

        return {
            "bonus": round(result.bonus or 0.0, 2),
            "penalty": round(result.penalty or 0.0, 2),
            "success_days": result.success_days or 0,
            "pending_days": result.pending_days or 0,
            "fail_days": result.fail_days or 0,
        }

    def get_monthly_activity_summary(self, username: str, start_date: date, end_date: date) -> dict[int, dict]:
        rows = self.db.query(
            extract("month", db_model.Activity.date).label("month"),
            func.count().label("activity_count"),
            func.sum(case((db_model.Activity.status == "success", 1), else_=0)).label("success_days"),
            func.sum(case((db_model.Activity.status == "failure", 1), else_=0)).label("fail_days"),
            func.sum(case((db_model.Activity.status == "pending", 1), else_=0)).label("pending_days"),
            func.coalesce(func.sum(db_model.Activity.bonus), 0).label("bonus"),
            func.coalesce(func.sum(db_model.Activity.penalty), 0).label("penalty"),
        ).filter(
            db_model.Activity.username == username,
            db_model.Activity.date >= start_date,
            db_model.Activity.date <= end_date,
        ).group_by(
            extract("month", db_model.Activity.date)
        ).all()

        return {
            int(row.month): {
                "success_days": row.success_days or 0,
                "fail_days": (row.fail_days or 0) + (row.pending_days or 0),
                "bonus": round_money_amount(row.bonus or 0.0),
                "penalty": round_money_amount(row.penalty or 0.0),
                "pay_adjustment": round_money_amount((row.bonus or 0.0) - (row.penalty or 0.0)),
            }
            for row in rows
        }
