import traceback
import uuid
from typing import Union
from datetime import timedelta
from sqlalchemy.orm import Session
from app.exceptions import NotAuthorized
from lib.log_conf import logger
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.error_codes import NotAuthorizedCode
from app.security.token import create_access_token, create_refresh_token_value
from app.security.password import verify_password


class LoginUseCase:
    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def execute(self, username: str, plain_password: str, device_id: str) -> dict:
        """ ユーザーが存在するか、パスワードが正しいかを確認し、アクセストークンとリフレッシュトークンを発行する

        Note:
            この内、routerからレスポンスで返すのはアクセストークン、トークンタイプ、ユーザーロールのみとし、
            リフレッシュトークンはセキュリティの観点からクッキーに保存する
            よって、LoginUserResponseとは別の辞書型で返す
        """
        user = self.user_repo.get_user(username)
        if not user:
            raise NotAuthorized(code=NotAuthorizedCode.LOGIN_FAILED)
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
