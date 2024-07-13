import os
from passlib.context import CryptContext
from typing import Union
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session
from jose import jwt, JWTError

# openssl rand -hex 32
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "ecd518ef9af267a68cd92ae2ba3e8570eae25c713a84dedf0b96066e7d73d205"
)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(db_model.User).filter(
        db_model.User.username == username).one()
    return user


def get_access_token(username: str):
    return create_access_token({"sub": username})


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print(to_encode)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="証明書を認証できませんでした",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        user = get_user(username, db)
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        return {"username": username}
    except JWTError:
        raise credentials_exception
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
