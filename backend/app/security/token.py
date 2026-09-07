import os
import traceback
from typing import Union
from datetime import datetime, timedelta, timezone
from app.exceptions import BadRequest
from lib.log_conf import logger
from jose import jwt
from app.error_codes import BadRequestCode

# openssl randex 32
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
# .envに定義したものは文字列として読み込まれるようなのでint型へ変換する
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_WEEKS = int(os.getenv("REFRESH_TOKEN_EXPIRE_WEEKS", 1))


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
        raise BadRequest(code=BadRequestCode.UNEXPECTED_ERROR)


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
