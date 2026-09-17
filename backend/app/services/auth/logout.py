from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import TokenRepository
from lib.log_conf import logger


class LogoutUseCase:
    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def execute(self, username: str, device_id: str) -> None:
        token = self.token_repo.get_refresh_token(username, device_id)
        if token:
            self.token_repo.delete_refresh_token(username, device_id)
        logger.info(f"{username}がログアウト")
