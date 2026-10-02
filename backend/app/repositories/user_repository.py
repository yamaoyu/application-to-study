from db import db_model
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime


class UserRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def insert_user(
            self,
            username: str,
            hash_password: str,
            email: Optional[str],
            role: str,
            created_at: datetime) -> None:
        form_data = db_model.User(
            username=username, password=hash_password, email=email, role=role, created_at=created_at)
        self.db.add(form_data)

    def get_user(self, username: str) -> db_model.User:
        return self.db.query(db_model.User).filter(
            db_model.User.username == username).one_or_none()

    def update_password(self, user: db_model.User, password: str) -> None:
        user.password = password

    def update_last_active_at(self, user: db_model.User, last_active_at: datetime):
        user.last_active_at = last_active_at

    def get_users(self,
                  status: Optional[str] = None,
                  last_active_at: Optional[datetime] = None,
                  created_at: Optional[datetime] = None,
                  role: Optional[str] = None,
                  username: Optional[str] = None) -> list:
        sqlstatement = self.db.query(
            db_model.User.username,
            db_model.User.role,
            db_model.User.status,
            db_model.User.created_at,
            db_model.User.last_active_at
        )
        if status:
            sqlstatement = sqlstatement.filter(db_model.User.status == status)
        if last_active_at:
            sqlstatement = sqlstatement.filter(db_model.User.last_active_at >= last_active_at)
        if created_at:
            sqlstatement = sqlstatement.filter(db_model.User.created_at >= created_at)
        if role:
            sqlstatement = sqlstatement.filter(db_model.User.role == role)
        if username:
            sqlstatement = sqlstatement.filter(db_model.User.username.like(f"%{username}%"))
        return sqlstatement.all()
