import os
import traceback
from app.exceptions import NotFound, NotAuthorized, Forbidden
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
            if user.must_change_password or user.token_version != payload.get("token_version"):
                raise Forbidden(code=NotAuthorizedCode.PASSWORD_CHANGE_REQUIRED)
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
            user = self.authenticate_user(token)
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        except ExpiredSignatureError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except JWTError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except Exception:
            logger.error(f"ユーザーの認証に失敗しました\n{traceback.format_exc()}")
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        if user.must_change_password:
            raise Forbidden(code=NotAuthorizedCode.PASSWORD_CHANGE_REQUIRED)
        if user.token_version != payload.get("token_version"):
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        return {
            "username": user.username,
            "role": user.role,
            "status": user.status,
            "token_version": user.token_version
        }

    def get_current_user_from_token_for_logout(self, token: str) -> dict:
        try:
            user = self.authenticate_user(token)
        except ExpiredSignatureError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except JWTError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except Exception:
            logger.error(f"ユーザーの認証に失敗しました\n{traceback.format_exc()}")
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        return {
            "username": user.username,
            "role": user.role,
            "status": user.status,
            "token_version": user.token_version
        }

    def get_current_user_for_password_change(self, token: str) -> dict:
        """
        管理者によるパスワードリセットされたユーザーがパスワード変更するための認証
        must_change_passwordがTrueでないと使えない
        """
        try:
            user = self.authenticate_user(token)
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        except ExpiredSignatureError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except JWTError:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        except Exception:
            logger.error(f"ユーザーの認証に失敗しました\n{traceback.format_exc()}")
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        if user.token_version != payload.get("token_version"):
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        if user.status != "active":
            raise Forbidden(code=NotAuthorizedCode.USER_SUSPENDED)
        if not user.must_change_password:
            raise Forbidden(code=NotAuthorizedCode.NOT_HAVE_PERMISSION)
        return {
            "username": user.username,
            "role": user.role,
            "status": user.status,
            "token_version": user.token_version
        }

    def authenticate_user(self, token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        return user
