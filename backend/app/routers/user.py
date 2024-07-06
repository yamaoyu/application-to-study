from fastapi import APIRouter, HTTPException, Depends
from db import db_model
from security import (get_password_hash,
                      verify_password,
                      create_access_token,)
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.user_model import UserInfo, ResponseCreatedUser
from sqlalchemy.exc import IntegrityError, NoResultFound


router = APIRouter()


@router.post("/registration", response_model=ResponseCreatedUser)
def create_user(user: UserInfo, db: Session = Depends(get_db)):
    try:
        user_id = user.user_id
        plain_password = user.password
        email = user.email
        if not (6 <= len(plain_password) <= 12):
            raise HTTPException(status_code=400,
                                detail="パスワードは6文字以上、12文字以下としてください")
        hash_password = get_password_hash(plain_password)
        user_info = db_model.User(
            user_id=user_id, password=hash_password, email=email)
        db.add(user_info)
        db.commit()
        db.refresh(user_info)
        return {"user_id": user.user_id,
                "password": len(user.password) * "*",
                "email": user.email,
                "message": f"{user_id}の作成に成功しました。"}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError:
        raise HTTPException(status_code=400,
                            detail="既に登録されています。")
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"ユーザー登録処理中にエラーが発生しました。{e}")


@router.post("/token")
def login(user: UserInfo, db: Session = Depends(get_db)):
    try:
        user_id = user.user_id
        plain_password = user.password
        user_info = db.query(db_model.User).filter(
            db_model.User.user_id == user_id).one()
        is_password = verify_password(plain_password, user_info.password)
        if not is_password:
            raise HTTPException(status_code=400, detail="パスワードが正しくありません。")
        token = create_access_token({"sub": user_id})
        return {"access_token": token, "token_type": "bearer"}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{user_id}は登録されていません。")
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ログイン処理に失敗しました。{e}")
