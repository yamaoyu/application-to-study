from logging import getLogger, basicConfig, INFO
from db import db_model
from security import (get_password_hash,
                      verify_password)
from db.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.models.user_model import UserInfo, ResponseCreatedUser
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from security import get_access_token


router = APIRouter()
basicConfig(level=INFO, format="%(levelname)s: %(message)s")
logger = getLogger(__name__)


def authenticate_user(username: str, plain_password: str,
                      db: Session = Depends(get_db)):
    try:
        user = db.query(db_model.User).filter(
            db_model.User.username == username).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        if not verify_password(plain_password, user.password):
            raise HTTPException(status_code=400, detail="パスワードが不正です")
        return True
    except HTTPException as http_e:
        raise http_e


@router.post("/register", response_model=ResponseCreatedUser)
def create_user(user: UserInfo, db: Session = Depends(get_db)):
    try:
        username = user.username
        plain_password = user.password
        email = user.email
        if not (6 <= len(plain_password) <= 12):
            raise HTTPException(status_code=400,
                                detail="パスワードは6文字以上、12文字以下としてください")
        hash_password = get_password_hash(plain_password)
        form_data = db_model.User(
            username=username, password=hash_password, email=email)
        db.add(form_data)
        db.commit()
        db.refresh(form_data)
        logger.info(f"ユーザー作成:{username}")
        return {"username": username,
                "password": len(plain_password) * "*",
                "email": user.email,
                "message": f"{username}の作成に成功しました。"}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,
                            detail="既に登録されています。")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,
                            detail=f"ユーザー登録処理中にエラーが発生しました。{e}")


@router.post("/login")
def login(user_info: UserInfo,
          db: Session = Depends(get_db)):
    """ ユーザー操作用 """
    username = user_info.username
    plain_password = user_info.password
    try:
        user = db.query(db_model.User).filter(
            db_model.User.username == username).one()
        is_password = verify_password(plain_password, user.password)
        if not is_password:
            raise HTTPException(status_code=400, detail="パスワードが正しくありません。")
        access_token = get_access_token(username)
        logger.info(f"{username}がログイン")
        return {"access_token": access_token, "token_type": "bearer"}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{username}は登録されていません。")
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ログイン処理に失敗しました。{e}")


@router.post("/token")
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """ APIでアクセストークン取得用 """
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = get_access_token(form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}
