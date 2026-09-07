from typing import Optional
from lib.log_conf import logger
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import UserRepository
from app.exceptions import Conflict
from app.models.user_model import RegisterUserResponse
from app.error_codes import ConflictCode
from app.security.password import get_password_hash
from app.domain.user.username import Username
from app.domain.user.password import PlainPassword
from app.domain.user.email import Email


class CreateUserUseCase():
    def __init__(self, db):
        self.user_repo = UserRepository(db)

    def execute(self,
                username_input: str,
                plain_password: str,
                email_input: Optional[str],
                role: str) -> RegisterUserResponse:
        username = Username(username_input)
        password = PlainPassword(plain_password)
        email = Email(email_input)
        hash_password = get_password_hash(password.value)
        try:
            self.user_repo.insert_user(username.value, hash_password, email.value, role)
            self.user_repo.flush()
        except IntegrityError as sqlalchemy_error:
            logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
            raise Conflict(code=ConflictCode.USER_ALREADY_EXISTS)
        logger.info(f"ユーザー作成:{username.value}")
        return RegisterUserResponse(
            username=username.value,
            password=len(plain_password) * "*",
            email=email.value,
            role=role
        )
