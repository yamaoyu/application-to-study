from app.domain.user.password import PlainPassword
from app.error_codes import NotAuthorizedCode, NotFoundCode
from app.exceptions import NotAuthorized, NotFound
from app.repositories.auth_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.security.password import get_password_hash, verify_password


class ChangePasswordUseCase:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.auth_repo = TokenRepository(db)

    def execute(self, old_password: str, new_password: str, username: str) -> None:
        validate_password = PlainPassword(new_password, field_name="new_password")
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        if not verify_password(old_password, user.password):
            raise NotAuthorized(code=NotAuthorizedCode.INVALID_CURRENT_PASSWORD)
        self.user_repo.update_password(user, get_password_hash(validate_password.value))
        self.auth_repo.delete_refresh_token(username)
        self.user_repo.flush()
