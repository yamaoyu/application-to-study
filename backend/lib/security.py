import os
import traceback
import re
import bcrypt
from typing import Union
from datetime import datetime, timedelta, timezone
from app.exceptions import BadRequest, NotAuthorized
from lib.log_conf import logger
from jose import jwt

# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
PEPPER = os.getenv("PEPPER")
# .envに定義したものは文字列として読み込まれるようなのでint型へ変換する
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_WEEKS = int(os.getenv("REFRESH_TOKEN_EXPIRE_WEEKS"))
ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))
special_characters = r"[!@#$%&*()+\-=[\]{};:<>,./?_~|]"

credentials_exception = NotAuthorized(detail="証明書を認証できませんでした")


def verify_password(plain_password, hashed_password) -> bool:
    pw = (plain_password + PEPPER).encode("utf-8")
    try:
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError) as e:
        logger.error(f"パスワードの検証に失敗しました{str(e)}")
        return False


def get_password_hash(password) -> str:
    pw = (password + PEPPER).encode("utf-8")
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt(rounds=ROUNDS))
    return hashed.decode("utf-8")


def is_password_complex(password: str) -> bool:
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(special_characters, password):
        return False
    return True


def create_access_token(payload: dict,
                        expires_delta: Union[timedelta, None] = None):
    try:
        to_encode = payload.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + \
                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        access_token = jwt.encode(
            to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return access_token
    except Exception:
        logger.error(f"アクセストークンの作成中にエラーが発生しました\n{traceback.format_exc()}")
        raise BadRequest(detail="トークンの作成に失敗しました")


def create_refresh_token_value(payload: dict, expires_delta: Union[timedelta, None] = None) -> tuple:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(weeks=REFRESH_TOKEN_EXPIRE_WEEKS)
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token, expire
