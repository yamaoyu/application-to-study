from datetime import datetime

from sqlalchemy.orm import Session

from app.models.admin_model import UserRole, UserStatus
from db import db_model


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def insert_user(
        self,
        username: str,
        hash_password: str,
        role: str,
        created_at: datetime,
        email: str | None = None,
    ) -> None:
        form_data = db_model.User(
            username=username,
            password=hash_password,
            email=email,
            role=role,
            created_at=created_at,
        )
        self.db.add(form_data)

    def get_user(self, username: str) -> db_model.User:
        return (
            self.db.query(db_model.User)
            .filter(db_model.User.username == username)
            .one_or_none()
        )

    def update_password(self, user: db_model.User, password: str) -> None:
        user.password = password
        user.must_change_password = False
        user.token_version += 1

    def update_last_active_at(self, user: db_model.User, last_active_at: datetime):
        user.last_active_at = last_active_at

    def get_users(
        self,
        status: str | None = None,
        last_active_at: datetime | None = None,
        created_at: datetime | None = None,
        role: str | None = None,
        username: str | None = None,
    ) -> list:
        sqlstatement = self.db.query(
            db_model.User.username,
            db_model.User.role,
            db_model.User.status,
            db_model.User.created_at,
            db_model.User.last_active_at,
        )
        if status:
            sqlstatement = sqlstatement.filter(db_model.User.status == status)
        if last_active_at:
            sqlstatement = sqlstatement.filter(
                db_model.User.last_active_at >= last_active_at
            )
        if created_at:
            sqlstatement = sqlstatement.filter(db_model.User.created_at >= created_at)
        if role:
            sqlstatement = sqlstatement.filter(db_model.User.role == role)
        if username:
            sqlstatement = sqlstatement.filter(
                db_model.User.username.like(f"%{username}%")
            )
        return sqlstatement.all()

    def change_status(self, user: db_model.User, status: UserStatus) -> None:
        user.status = status

    def count_active_admin_number(self) -> int:
        # 同時にリクエスト来た時に備えて悲観ロックをする
        # 仮にリクエストが多い場合は管理者ユーザー数を保持するテーブルを作ってそれをロックするなどがある
        admins = (
            self.db.query(db_model.User)
            .filter(db_model.User.role == "admin", db_model.User.status == "active")
            .with_for_update()
            .all()
        )

        return len(admins)

    def change_role(self, user: db_model.User, role: UserRole) -> None:
        user.role = role

    def reset_password(self, user: db_model.User, hashed_password: str) -> None:
        """トークンバージョンを見てアクセストークンの有効性を確認するため,パスワードリセット時に加算"""
        user.password = hashed_password
        user.must_change_password = True
        user.token_version += 1
