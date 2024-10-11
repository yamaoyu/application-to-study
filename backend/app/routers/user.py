import traceback
from db import db_model
from lib.security import (get_password_hash,
                          verify_password)
from db.database import get_db
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.models.user_model import UserInfo, ResponseCreatedUser
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi import APIRouter, HTTPException, Depends
from lib.security import get_token, get_current_user, admin_only


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
    except Exception:
        logger.error(f"ユーザー認証に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/users", response_model=ResponseCreatedUser, status_code=201)
def create_user(user: UserInfo, db: Session = Depends(get_db)):
    try:
        username = user.username
        plain_password = user.password
        email = user.email
        valid_roles = ["admin", "general"]
        role = user.role if user.role in valid_roles else "general"
        if not (6 <= len(plain_password) <= 12):
            raise HTTPException(status_code=400,
                                detail="パスワードは6文字以上、12文字以下としてください")
        hash_password = get_password_hash(plain_password)
        form_data = db_model.User(
            username=username, password=hash_password, email=email, role=role)
        db.add(form_data)
        db.commit()
        db.refresh(form_data)
        logger.info(f"ユーザー作成:{username}")
        return {"username": username,
                "password": len(plain_password) * "*",
                "email": user.email,
                "message": f"{username}の作成に成功しました",
                "role": role if role else "general"}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "for key 'users.PRIMARY'" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400,
                                detail="そのユーザー名は既に登録されています")
        elif "for key 'users.email'" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400,
                                detail="そのメールアドレスは既に登録されています")
        else:
            logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
            raise HTTPException(status_code=400, detail="ユーザーの作成に失敗しました")
    except Exception:
        logger.error(f"ユーザー作成に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/admins", response_model=ResponseCreatedUser, status_code=201)
@admin_only()
def create_admin_user(user: UserInfo,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    try:
        username = user.username
        plain_password = user.password
        email = user.email
        if not (6 <= len(plain_password) <= 12):
            raise HTTPException(status_code=400,
                                detail="パスワードは6文字以上、12文字以下としてください")
        hash_password = get_password_hash(plain_password)
        form_data = db_model.User(
            username=username, password=hash_password,
            email=email, role="admin")
        db.add(form_data)
        db.commit()
        db.refresh(form_data)
        logger.info(f"ユーザー作成:{username}")
        return {"username": username,
                "password": len(plain_password) * "*",
                "email": user.email,
                "message": f"管理者ユーザー「{username}」の作成に成功しました",
                "role": "admin"}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "for key 'users.PRIMARY'" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400,
                                detail="そのユーザー名は既に登録されています")
        elif "for key 'users.email'" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400,
                                detail="そのメールアドレスは既に登録されています")
        else:
            logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
            raise HTTPException(status_code=400, detail="ユーザーの作成に失敗しました")
    except Exception:
        logger.error(f"ユーザー作成に失敗しました\n{traceback.format_exc()}")
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
        access_token = get_token(user, token_type="access")
        refresh_token = get_token(user, token_type="refresh", db=db)
        logger.info(f"{username}がログイン")
        return {"access_token": access_token,
                "token_type": "Bearer",
                "refresh_token": refresh_token}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{username}は登録されていません")
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"ログイン処理に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/logout", status_code=200)
def logout(current_user: dict = Depends(get_current_user),
           db: Session = Depends(get_db)):
    try:
        username = current_user['username']
        token = db.query(db_model.Token).filter(
            db_model.Token.username == username).one()
        token.status = False
        db.commit()
        logger.info(f"{username}がログアウト")
        return {"message": f"{username}がログアウト"}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{username}は登録されていません")
    except Exception:
        logger.error(f"ログイン処理に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
