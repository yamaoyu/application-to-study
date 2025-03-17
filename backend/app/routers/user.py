import traceback
from db import db_model
from lib.security import (get_password_hash, get_token, get_current_user,
                          admin_only, verify_password, verify_refresh_token)
from db.database import get_db
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.models.user_model import RegisterUserInfo, ResponseCreatedUser, LoginUserInfo, ChangePasswordInfo
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi import APIRouter, HTTPException, Depends, Response, Cookie


router = APIRouter()
response = Response()


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
def create_user(user: RegisterUserInfo, db: Session = Depends(get_db)):
    try:
        username = user.username
        plain_password = user.password
        email = user.email
        role = user.role if user.role == "admin" else "general"
        hash_password = get_password_hash(plain_password)
        form_data = db_model.User(
            username=username, password=hash_password, email=email, role=role)
        db.add(form_data)
        db.commit()
        logger.info(f"ユーザー作成:{username}")
        return {"username": username,
                "password": len(plain_password) * "*",
                "email": user.email,
                "message": f"{username}の作成に成功しました",
                "role": role if role == "admin" else "general"}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
        raise HTTPException(
            status_code=400, detail="入力された情報は既に使用されています。\n別のユーザー名またはメールアドレスをお試しください")
    except Exception:
        logger.error(f"ユーザー作成に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/admins", response_model=ResponseCreatedUser, status_code=201)
@admin_only()
def create_admin_user(user: RegisterUserInfo,
                      db: Session = Depends(get_db)):
    try:
        username = user.username
        plain_password = user.password
        email = user.email
        hash_password = get_password_hash(plain_password)
        form_data = db_model.User(
            username=username, password=hash_password,
            email=email, role="admin")
        db.add(form_data)
        db.commit()
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
        logger.warning(f"ユーザー作成に失敗しました\n{str(sqlalchemy_error)}")
        raise HTTPException(
            status_code=400, detail="入力された情報は既に使用されています。\n別のユーザー名またはメールアドレスをお試しください")
    except Exception:
        logger.error(f"ユーザー作成に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/login", status_code=200)
def login(user_info: LoginUserInfo,
          db: Session = Depends(get_db),
          device_id: str = Cookie(default=None),
          response: Response = response):
    username = user_info.username
    plain_password = user_info.password
    wrong_info_msg = "入力情報が正しくありません。\nユーザー名またはパスワードをご確認ください"
    try:
        user = db.query(db_model.User).filter(
            db_model.User.username == username).one()
        is_password = verify_password(plain_password, user.password)
        if not is_password:
            raise HTTPException(status_code=401, detail=wrong_info_msg)
        access_token = get_token(user, token_type="access")
        refresh_token = get_token(user, token_type="refresh",
                                  response=response, db=db, device_id=device_id)
        logger.info(f"{username}がログイン")
        return {"access_token": access_token,
                "token_type": "Bearer",
                "refresh_token": refresh_token}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=wrong_info_msg)
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"ログイン処理に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/logout", status_code=200)
def logout(device_id: str = Cookie(default=None),
           current_user: dict = Depends(get_current_user),
           db: Session = Depends(get_db),
           response: Response = response):
    try:
        username = current_user['username']
        db.query(db_model.Token).filter(db_model.Token.username == username,
                                        db_model.Token.device_id == device_id).delete()
        db.commit()
        logger.info(f"{username}がログアウト")
        response.delete_cookie(key="refresh_token")
        response.delete_cookie(key="device_id")
        return {"message": f"{username}がログアウト"}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{username}は登録されていません")
    except Exception:
        logger.error(f"ログイン処理に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/token", status_code=200)
def regenerate_access_token(refresh_token: str = Cookie(default=None),
                            device_id: str = Cookie(default=None),
                            db: Session = Depends(get_db)):
    """ アクセストークンの期限が切れている場合、リフレッシュトークンを使ってアクセストークンを再発行する """
    try:
        # アクセストークンは切れているため、リフレッシュトークンを使用してユーザーを取得する
        current_user = get_current_user(refresh_token, db=db)
        user = db.query(db_model.User).filter(
            db_model.User.username == current_user["username"]).one()
        if not user:
            raise HTTPException(status_code=404,
                                detail="再度ログインしてください")
        if verify_refresh_token(refresh_token, device_id=device_id, db=db):
            return {"access_token": get_token(user, token_type="access"),
                    "token_type": "Bearer"}
        else:
            raise HTTPException(status_code=401)
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"トークンの再発行に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/password", status_code=200)
def change_password(change_password_info: ChangePasswordInfo,
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    try:
        old_password = change_password_info.old_password
        new_password = change_password_info.new_password
        user = db.query(db_model.User).filter(
            db_model.User.username == current_user["username"]).one()
        if not verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="パスワードが正しくありません")
        user.password = get_password_hash(new_password)
        db.commit()
        return {"message": "パスワードの変更に成功しました"}
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    except Exception:
        logger.error(f"パスワード変更に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
