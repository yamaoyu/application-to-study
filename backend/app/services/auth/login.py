import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.error_codes import NotAuthorizedCode
from app.exceptions import Forbidden, NotAuthorized
from app.repositories.auth_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.security.password import verify_password
from app.security.token import create_access_token, create_refresh_token_value
from lib.log_conf import logger


class LoginUseCase:
    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def execute(self, username: str, plain_password: str, device_id: str) -> dict:
        """ユーザーが存在するか、パスワードが正しいかを確認し、アクセストークンとリフレッシュトークンを発行する

        Note:
            この内、routerからレスポンスで返すのはアクセストークン、トークンタイプ、ユーザーロールのみとし、
            リフレッシュトークンはセキュリティの観点からクッキーに保存する
            よって、クッキーに保存する用とAPIが返す用のデータを合わせて返す
        """
        user = self.user_repo.get_user(username)
        if not user:
            raise NotAuthorized(code=NotAuthorizedCode.LOGIN_FAILED)
        if user.status != "active":
            raise Forbidden(code=NotAuthorizedCode.USER_SUSPENDED)
        is_password = verify_password(plain_password, user.password)
        if not is_password:
            raise NotAuthorized(code=NotAuthorizedCode.LOGIN_FAILED)
        access_token = create_access_token(
            {
                "sub": user.username,
                "role": user.role,
                "token_version": user.token_version,
            }
        )
        token_info = self.create_or_update_refresh_token(
            {
                "sub": user.username,
                "role": user.role,
                "token_version": user.token_version,
            },
            device_id=device_id,
        )
        logger.info(f"{username}がログイン")
        # リフレッシュトークンがあり、ログインフォームからログインする頻度は少ないのでdb書き込みによるパフォーマンスの影響は問題ない
        now = datetime.now()
        self.user_repo.update_last_active_at(user, now)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "refresh_token": token_info["refresh_token"],
            "device_id": token_info["device_id"],
            "expires_at": token_info["expires_at"],
            "role": user.role,
            "must_change_password": user.must_change_password,
        }

    def create_or_update_refresh_token(
        self, data: dict, device_id: str, expires_delta: timedelta | None = None
    ):
        refresh_token, expire = create_refresh_token_value(data, expires_delta)
        if not device_id:
            # device_idがない場合は新規発行、ある場合は既存のdevice_idを使用して更新する
            device_id = str(uuid.uuid4())
        self.token_repo.create_or_update_refresh_token(
            username=data["sub"],
            device_id=device_id,
            refresh_token=refresh_token,
            expires_at=expire,
        )
        self.token_repo.db.flush()
        return {
            "refresh_token": refresh_token,
            "device_id": device_id,
            "expires_at": expire,
        }
