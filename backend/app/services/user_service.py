from lib.security import (get_password_hash, get_token, get_current_user,
                          verify_password, verify_refresh_token)
from lib.log_conf import logger
from sqlalchemy.exc import IntegrityError
from fastapi import Response
from app.repositories.user_repository import UserRepository
from app.exceptions import NotFound, Conflict, NotAuthorized


class UserService():
    def __init__(self, db):
        self.repo = UserRepository(db)

    def create_user(self, username: str, plain_password: str, email: str, role: str) -> dict:
        hash_password = get_password_hash(plain_password)
        try:
            self.repo.insert_user(username, hash_password, email, role)
            self.repo.flush()
        except IntegrityError as sqlalchemy_error:
            logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
            raise Conflict(detail="入力された情報は既に使用されています。\n別のユーザー名またはメールアドレスをお試しください")
        logger.info(f"ユーザー作成:{username}")
        return {
            "username": username,
            "password": len(plain_password) * "*",
            "email": email,
            "message": f"{username}の作成に成功しました",
            "role": role
        }

    def login(self, username: str, plain_password: str, device_id: str, response: Response) -> dict:
        wrong_info_msg = "入力情報が正しくありません。\nユーザー名またはパスワードをご確認ください"
        user = self.repo.get_user(username)
        if not user:
            raise NotFound(detail=wrong_info_msg)
        is_password = verify_password(plain_password, user.password)
        if not is_password:
            raise NotAuthorized(detail=wrong_info_msg)
        access_token = get_token(user, token_type="access")
        refresh_token = get_token(user, token_type="refresh",
                                  response=response, db=self.repo.db, device_id=device_id)
        logger.info(f"{username}がログイン")
        return {"access_token": access_token,
                "token_type": "Bearer",
                "refresh_token": refresh_token,
                "role": user.role}

    def logout(self, username: str, device_id: str, response: Response) -> dict:
        token = self.repo.get_token(username, device_id)
        if token:
            self.repo.delete_token(username, device_id)
        logger.info(f"{username}がログアウト")
        response.delete_cookie(key="refresh_token")
        response.delete_cookie(key="device_id")
        return {"message": f"{username}がログアウト"}

    def regenerate_access_token(self, refresh_token: str, device_id: str) -> dict:
        # アクセストークンは切れているため、リフレッシュトークンを使用してユーザーを取得する
        current_user = get_current_user(refresh_token, db=self.repo.db)
        user = self.repo.get_user(current_user["username"])
        if not user:
            raise NotFound(detail="再度ログインしてください")
        if verify_refresh_token(refresh_token, device_id=device_id, db=self.repo.db):
            return {"access_token": get_token(user, token_type="access"),
                    "token_type": "Bearer"}
        else:
            raise NotAuthorized(detail="再度ログインしてください")

    def change_password(self, old_password: str, new_password: str, username: str):
        user = self.repo.get_user(username)
        if not user:
            raise NotFound(detail="ユーザーが見つかりません")
        if not verify_password(old_password, user.password):
            raise NotAuthorized(detail="パスワードが正しくありません")
        user.password = get_password_hash(new_password)
        return {"message": "パスワードの変更に成功しました"}
