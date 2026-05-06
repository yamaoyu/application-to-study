from db import db_model
from sqlalchemy.orm import Session


class UserRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def insert_user(self, username: str, hash_password: str, email: str, role: str) -> None:
        form_data = db_model.User(
            username=username, password=hash_password, email=email, role=role)
        self.db.add(form_data)

    def get_user(self, username: str) -> db_model.User:
        return self.db.query(db_model.User).filter(
            db_model.User.username == username).one_or_none()

    def update_password(self, user: db_model.User, password: str) -> None:
        user.password = password
