from sqlalchemy.orm import Session
from app.exceptions import NotFound, NotAuthorized
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.error_codes import NotAuthorizedCode, NotFoundCode
from app.models.user_model import regenerateAccessTokenResponse
from app.security.token import create_access_token
from app.services.auth.token_verifier import TokenVerifier


class RegenerateAccessTokenUseCase:
    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.token_verifier = TokenVerifier(db)

    def execute(self, refresh_token: str, device_id: str) -> regenerateAccessTokenResponse:
        # アクセストークンは切れているため、リフレッシュトークンを使用してユーザーを取得する
        current_user = self.token_verifier.get_current_user_from_token(refresh_token)
        user = self.user_repo.get_user(current_user["username"])
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        if self.token_verifier.verify_refresh_token(refresh_token, device_id=device_id):
            access_token = create_access_token({"sub": user.username, "role": user.role})
            return regenerateAccessTokenResponse(access_token=access_token, token_type="Bearer")
        else:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
