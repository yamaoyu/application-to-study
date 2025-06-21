import os
import uuid
import traceback
import re
from passlib.context import CryptContext
from typing import Union
from functools import wraps
from datetime import datetime, timedelta, timezone, date
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Response
from db import db_model
from db.database import get_db
from lib.log_conf import logger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError

# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
PEPPER = os.getenv("PEPPER")
# .envに定義したものは文字列として読み込まれるようなのでint型へ変換する
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_WEEKS = int(os.getenv("REFRESH_TOKEN_EXPIRE_WEEKS"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
special_characters = r"[!@#$%&*()+\-=[\]{};:<>,./?_~|]"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="証明書を認証できませんでした",
    headers={"WWW-Authenticate": "Bearer"}
)


def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(db_model.User).filter(
        db_model.User.username == username).one_or_none()
    if not user:
        raise NoResultFound(f"{username}は登録されていません")
    return user


def get_token(user: db_model, token_type: str, response: Response = None, db=None, device_id: str = None):
    if token_type == "access":
        return create_access_token({"sub": user.username,
                                    "role": user.role})
    elif token_type == "refresh":
        return create_refresh_token({"sub": user.username,
                                     "role": user.role}, response=response, db=db, device_id=device_id)
    else:
        logger.error(f"無効なトークンタイプ: {token_type}")
        raise HTTPException(status_code=401, detail="無効なトークンタイプです")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify((plain_password + PEPPER), hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password + PEPPER)


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


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + \
                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        access_token = jwt.encode(
            to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return access_token
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"アクセストークンの作成中にエラーが発生しました\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="トークンの作成に失敗しました")


def create_refresh_token(data: dict,
                         response: Response,
                         expires_delta: Union[timedelta, None] = None,
                         db: Session = Depends(get_db),
                         device_id: str = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + \
                timedelta(weeks=REFRESH_TOKEN_EXPIRE_WEEKS)
        to_encode.update({"exp": expire})
        refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        if device_id:
            # トークンが既に存在するか確認(リフレッシュトークンはユーザーとデバイスで一意)
            existing_token = db.query(db_model.Token).filter(
                db_model.Token.username == data["sub"],
                db_model.Token.device_id == device_id).one_or_none()
            # 既存のトークンがある場合は、トークンを更新
            if existing_token:
                existing_token.token = refresh_token
                existing_token.expires_at = expire
                existing_token.device_id = device_id
            else:
                new_token = db_model.Token(token=refresh_token,
                                           username=data["sub"],
                                           device_id=device_id,
                                           expires_at=expire)
                db.add(new_token)
        # デバイスIDが存在しない場合は、新規作成
        else:
            device_id = str(uuid.uuid4())
            new_token = db_model.Token(token=refresh_token,
                                       username=data["sub"],
                                       device_id=device_id,
                                       expires_at=expire)
            db.add(new_token)
        db.commit()
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            secure=True,
            httponly=True,
            expires=expire)
        response.set_cookie(
            key="device_id",
            value=device_id,
            secure=True,
            httponly=True)
        return refresh_token
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"リフレッシュトークンの作成中にエラーが発生しました\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="トークンの作成に失敗しました")


def verify_refresh_token(refresh_token: str,
                         device_id: str = None,
                         db: Session = Depends(get_db)):
    """ リフレッシュトークンを検証する """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
            return False
        user = get_user(username, db)
        if not user:
            return False
        fetch_token = db.query(db_model.Token).filter(
            db_model.Token.username == username, db_model.Token.device_id == device_id).one_or_none()
        if not fetch_token:
            return False
        if fetch_token.expires_at < date.today():
            return False
        if refresh_token != fetch_token.token:
            return False
        return True
    except Exception:
        logger.error(f"リフレッシュトークンの検証中にエラーが発生しました\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="リフレッシュトークンの検証に失敗しました")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="ユーザー名を取得できませんでした")
        user = get_user(username, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
        return {"username": username, "role": user.role}
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="再度ログインしてください")
    except JWTError:
        raise credentials_exception
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"ユーザーの認証に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="ユーザーの認証に失敗しました")


def admin_only():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = kwargs["current_user"]["role"]
            if role == "admin":
                return func(*args, **kwargs)
            else:
                raise HTTPException(
                    status_code=403, detail="管理者権限を持つユーザー以外はアクセスできません")
        return wrapper
    return decorator


def login_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token = kwargs["token"]
                db = kwargs["db"]
                payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
                username = payload.get("sub")
                if username is None:
                    raise credentials_exception
                user = get_user(username, db)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
                return func(*args, **kwargs)
            except ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="再度ログインしてください")
            except JWTError:
                raise credentials_exception
        return wrapper
    return decorator
