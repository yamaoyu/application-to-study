import os
import traceback
from app.exceptions import NotFound, NotAuthorized
from lib.log_conf import logger
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import date
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import TokenRepository
from app.error_codes import NotAuthorizedCode, NotFoundCode
# openssl rand -hex 32
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]


class TokenVerifier:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def verify_refresh_token(self, refresh_token: str, device_id: str) -> bool:
        """ リフレッシュトークンを検証する """
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM)
            username = payload.get("sub")
            if username is None:
                return False
            user = self.user_repo.get_user(username)
            if not user:
                return False
            fetch_token = self.token_repo.get_refresh_token(username, device_id)
            if not fetch_token:
                return False
            if fetch_token.expires_at < date.today():
                return False
            if refresh_token != fetch_token.token:
                return False
            return True
        except Exception:
            logger.error(f"リフレッシュトークンの検証中にエラーが発生しました\n{traceback.format_exc()}")
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)

    def get_current_user_from_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            username = payload.get("sub")
            if username is None:
                raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
            user = self.user_repo.get_user(username)
            if not user:
                raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
            return {"username": username, "role": user.role}
        except ExpiredSignatureError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except JWTError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except NotAuthorized as http_e:
            raise http_e
        except Exception:
            logger.error(f"ユーザーの認証に失敗しました\n{traceback.format_exc()}")
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
