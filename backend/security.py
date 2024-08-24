import os
from passlib.context import CryptContext
from typing import Union
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from db import db_model
from db.database import get_db
from log_conf import logger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError

# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(db_model.User).filter(
        db_model.User.username == username).one_or_none()
    if not user:
        raise NoResultFound(f"{username}は登録されていません")
    return user


def get_token(username: str, token_type: str, db=None):
    if token_type == "access":
        return create_access_token({"sub": username})
    elif token_type == "refresh":
        return create_refresh_token({"sub": username}, db=db)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None):
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + \
                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        if SECRET_KEY and ALGORITHM:
            return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        else:
            raise HTTPException(status_code=400,
                                detail="SECRET_KEYかALGORITHMが環境変数に設定されていません")
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.warning(f"アクセストークンの作成中にエラーが発生しました\n{str(e)}")
        raise HTTPException(status_code=500, detail="トークンの作成に失敗しました")


def create_refresh_token(data: dict,
                         expires_delta: Union[timedelta, None] = None,
                         db: Session = Depends(get_db)):
    REFRESH_TOKEN_EXPIRE_WEEKS = 2
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + \
                timedelta(weeks=REFRESH_TOKEN_EXPIRE_WEEKS)
        to_encode.update({"exp": expire})
        if SECRET_KEY and ALGORITHM:
            refresh_token = jwt.encode(
                to_encode, SECRET_KEY, algorithm=ALGORITHM)
        else:
            raise HTTPException(status_code=400,
                                detail="SECRET_KEYかALGORITHMが環境変数に設定されていません")
        # トークンが既に存在するか確認(リフレッシュトークンは1ユーザーに1つ)
        existing_token = db.query(db_model.Token).filter(
            db_model.Token.username == data["sub"]).one_or_none()
        # 既存のトークンがある場合は、トークンを更新
        if existing_token:
            existing_token.token = refresh_token
            existing_token.expires_at = expire
            existing_token.status = True
            db.commit()
        # トークンが存在しない場合は、新規作成
        else:
            new_token = db_model.Token(token=refresh_token,
                                       username=data["sub"],
                                       expires_at=expire)
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
        return refresh_token
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.warning(f"リフレッシュトークンの作成中にエラーが発生しました\n{str(e)}")
        raise HTTPException(status_code=500, detail="トークンの作成に失敗しました")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="証明書を認証できませんでした",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        if not SECRET_KEY or not ALGORITHM:
            raise HTTPException(status_code=500,
                                detail="SECRET_KEYかALGORITHMが環境変数に設定されていません")
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        user = get_user(username, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
        return {"username": username}
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="再度ログインしてください")
    except JWTError:
        raise credentials_exception
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.warning(f"トークンの作成中にエラーが発生しました{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="ユーザーの認証に失敗しました")
