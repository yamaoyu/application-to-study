from app.error_codes import NotAuthorizedCode, NotFoundCode
from app.exceptions import Forbidden, NotFound
from app.models.admin_model import ResetPasswordResponse
from app.repositories.auth_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.security.password import generate_random_password, get_password_hash


class ResetPassword:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)
        self.auth_repo = TokenRepository(db)

    def execute(
        self, target_username: str, requester_username: str
    ) -> ResetPasswordResponse:
        user = self.user_repo.get_user(target_username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)

        if user.username == requester_username:
            raise Forbidden(code=NotAuthorizedCode.CANNOT_RESET_OWN_PASSWORD)

        random_password = generate_random_password(16)
        hashed_password = get_password_hash(random_password)
        self.user_repo.reset_password(user, hashed_password)

        self.auth_repo.delete_refresh_token(target_username)

        return ResetPasswordResponse(username=target_username, password=random_password)
