from db import db_model
from security import (get_password_hash,
                      verify_password)
from db.database import get_db
from log_conf import logger
from typing import Annotated
from sqlalchemy.orm import Session
from app.models.user_model import UserInfo, ResponseCreatedUser
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from security import get_token


router = APIRouter()


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
    except Exception as e:
        logger.warning(f"ユーザー認証に失敗しました\n{str(e)}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/register", response_model=ResponseCreatedUser, status_code=201)
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
                "message": f"{username}の作成に成功しました"}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,
                            detail="既に登録されています")
    except Exception as e:
        logger.warning(f"ユーザー作成に失敗しました\n{str(e)}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/login", status_code=200)
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
            raise HTTPException(status_code=401, detail="パスワードが正しくありません")
        access_token = get_token(username, token_type="access")
        refresh_token = get_token(username, token_type="refresh", db=db)
        logger.info(f"{username}がログイン")
        return {"access_token": access_token,
                "token_type": "Bearer",
                "refresh_token": refresh_token}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{username}は登録されていません")
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.warning(f"ログイン処理に失敗しました\n{str(e)}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/token")
def refresh_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """ APIでアクセス・リフレッシュトークン更新用 """
    access_token = get_token(form_data.username, token_type="access")
    refresh_token = get_token(form_data.username, token_type="refresh")
    return {"access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token}
