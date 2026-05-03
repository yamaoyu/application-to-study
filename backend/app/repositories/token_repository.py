from db import db_model
from sqlalchemy.orm import Session


class TokenRepository():
    def __init__(self, db: Session) -> None:
        self.db = db

    def flush(self) -> None:
        self.db.flush()

    def get_refresh_token(self, username: str, device_id: str) -> db_model.Token:
        return self.db.query(db_model.Token).filter(
            db_model.Token.username == username,
            db_model.Token.device_id == device_id).one_or_none()

    def create_or_update_refresh_token(self, username: str, device_id: str, refresh_token: str, expires_at):
        existing_token = self.get_refresh_token(username, device_id)
        if existing_token:
            existing_token.token = refresh_token
            existing_token.expires_at = expires_at
            existing_token.device_id = device_id
        else:
            new_token = db_model.Token(token=refresh_token,
                                       username=username,
                                       device_id=device_id,
                                       expires_at=expires_at)
            self.db.add(new_token)

    def delete_refresh_token(self, username: str, device_id: str) -> None:
        self.db.query(db_model.Token).filter(
            db_model.Token.username == username,
            db_model.Token.device_id == device_id).delete()
