from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import TokenRepository
from app.error_codes import NotFoundCode
from app.exceptions import NotFound
from app.models.admin_model import ResetPasswordResponse
from app.security.password import get_password_hash, generate_random_password


class ResetPassword:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)
        self.auth_repo = TokenRepository(db)

    def execute(self, username: str) -> ResetPasswordResponse:
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)

        random_password = generate_random_password(16)
        hashed_password = get_password_hash(random_password)
        self.user_repo.reset_password(user, hashed_password)

        self.auth_repo.delete_refresh_token(username)

        return ResetPasswordResponse(
            username=username,
            password=random_password
        )
