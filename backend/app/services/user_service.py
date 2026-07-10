import os
import traceback
import uuid
from typing import Union, Optional
from lib.security import get_password_hash, verify_password, create_access_token, create_refresh_token_value
from lib.log_conf import logger
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.exceptions import NotFound, Conflict, NotAuthorized
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import date, timedelta
from app.models.user_model import (RegisterUserResponse,
                                   regenerateAccessTokenResponse)
from app.error_codes import NotAuthorizedCode, ConflictCode, NotFoundCode

# openssl rand -hex 32
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]


class UserService():
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def get_user(self, username: str):
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        return user

    def create_user(self,
                    username: str,
                    plain_password: str,
                    email: Optional[str],
                    role: str) -> RegisterUserResponse:
        hash_password = get_password_hash(plain_password)
        try:
            self.user_repo.insert_user(username, hash_password, email, role)
            self.user_repo.flush()
        except IntegrityError as sqlalchemy_error:
            logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
            raise Conflict(code=ConflictCode.USER_ALREADY_EXISTS)
        logger.info(f"ユーザー作成:{username}")
        return RegisterUserResponse(
            username=username,
            password=len(plain_password) * "*",
            email=email,
            role=role
        )

    def login(self, username: str, plain_password: str, device_id: str) -> dict:
        """ ユーザーが存在するか、パスワードが正しいかを確認し、アクセストークンとリフレッシュトークンを発行する

        Note:
            この内、routerからレスポンスで返すのはアクセストークン、トークンタイプ、ユーザーロールのみとし、
            リフレッシュトークンはセキュリティの観点からクッキーに保存する
            よって、LoginUserResponseとは別の辞書型で返す
        """
        user = self.get_user(username)
        is_password = verify_password(plain_password, user.password)
        if not is_password:
            raise NotAuthorized(code=NotAuthorizedCode.LOGIN_FAILED)
        access_token = create_access_token({"sub": user.username, "role": user.role})
        token_info = self.create_or_update_refresh_token(
            {"sub": user.username, "role": user.role}, device_id=device_id)
        logger.info(f"{username}がログイン")
        return {"access_token": access_token,
                "token_type": "Bearer",
                "refresh_token": token_info["refresh_token"],
                "device_id": token_info["device_id"],
                "expires_at": token_info["expires_at"],
                "role": user.role}

    def logout(self, username: str, device_id: str) -> None:
        token = self.token_repo.get_refresh_token(username, device_id)
        if token:
            self.token_repo.delete_refresh_token(username, device_id)
        logger.info(f"{username}がログアウト")

    def regenerate_access_token(self, refresh_token: str, device_id: str) -> regenerateAccessTokenResponse:
        # アクセストークンは切れているため、リフレッシュトークンを使用してユーザーを取得する
        current_user = self.get_current_user_from_token(refresh_token)
        user = self.get_user(current_user["username"])
        if self.verify_refresh_token(refresh_token, device_id=device_id):
            access_token = create_access_token({"sub": user.username, "role": user.role})
            return regenerateAccessTokenResponse(access_token=access_token, token_type="Bearer")
        else:
            raise NotAuthorized(code=NotAuthorizedCode.NOT_AUTHORIZED)

    def change_password(self, old_password: str, new_password: str, username: str) -> None:
        user = self.get_user(username)
        if not verify_password(old_password, user.password):
            raise NotAuthorized(code=NotAuthorizedCode.INVALID_CURRENT_PASSWORD)
        self.user_repo.update_password(user, get_password_hash(new_password))
        self.user_repo.flush()

    def create_or_update_refresh_token(self, data: dict,
                                       device_id: str,
                                       expires_delta: Union[timedelta, None] = None):
        try:
            refresh_token, expire = create_refresh_token_value(data, expires_delta)
            if not device_id:
                # device_idがない場合は新規発行、ある場合は既存のdevice_idを使用して更新する
                device_id = str(uuid.uuid4())
            self.token_repo.create_or_update_refresh_token(
                username=data["sub"],
                device_id=device_id,
                refresh_token=refresh_token,
                expires_at=expire
            )
            self.token_repo.db.flush()
            return {
                "refresh_token": refresh_token,
                "device_id": device_id,
                "expires_at": expire,
            }
        except Exception:
            logger.error(f"リフレッシュトークンの作成中にエラーが発生しました\n{traceback.format_exc()}")
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

    def verify_refresh_token(self, refresh_token: str,
                             device_id: str) -> bool:
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
