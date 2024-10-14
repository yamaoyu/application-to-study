import traceback
from datetime import datetime
from db.database import get_db
from db import db_model
from lib.check_data import set_date_format
from lib.log_conf import logger
from lib.security import (get_current_user, admin_only, login_required,
                          oauth2_scheme)
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.models.inquiry_model import (InquiryForm, ResponseInquiry,
                                      Category, Priority, EditInquiry)


router = APIRouter()


def check_data(category, detail):
    """ 問い合わせフォームのデータに不備がないかを確認する """
    if category not in Category.__members__.values():
        raise HTTPException(status_code=400, detail="カテゴリは選択肢から選択してください")
    if len(detail) > 256:
        raise HTTPException(status_code=400, detail="詳細は256文字以内で入力してください")


@router.post("/inquiries", status_code=201, response_model=ResponseInquiry)
@login_required()
def send_inquiry(param: InquiryForm,
                 db: Session = Depends(get_db),
                 token: str = Depends(oauth2_scheme)):
    try:
        category = param.category.value
        detail = param.detail
        date = datetime.today()
        check_data(category, detail)
        fetch_data = db.query(db_model.Inquiry).filter(
            db_model.Inquiry.category == category,
            db_model.Inquiry.detail == detail).one_or_none()
        # 同じ内容で登録があれば日付を更新
        if fetch_data:
            fetch_data.date = date
            db.commit()
        # 同じ内容で登録がなければ追加
        else:
            insert_data = db_model.Inquiry(category=category,
                                           detail=detail,
                                           date=date)
            db.add(insert_data)
            db.commit()
            db.refresh(insert_data)
            logger.info("問い合わせを受付")
        return {
            "category": category,
            "detail": detail,
            "message": "こちらの内容で受け付けました"
        }
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/inquiries")
@admin_only()
def get_inquiries(year: Optional[str] = None,
                  month: Optional[str] = None,
                  category: Optional[Category] = None,
                  priority: Optional[Priority] = None,
                  is_checked: Optional[bool] = None,
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    try:
        if not year and month:
            raise HTTPException(status_code=400, detail="月を指定する場合は年も指定してください")
        # インプットに応じてsql文を作成
        sqlstatement = db.query(db_model.Inquiry)
        if year and month:
            year_month = set_date_format(year, month)
            start_date = datetime(int(year), int(month), 1).date()
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date()
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date()
            sqlstatement = sqlstatement.filter(
                db_model.Inquiry.date.between(start_date, end_date))
        if category:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.category == category)
        if priority:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.priority == priority)
        if is_checked is not None:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.is_checked == is_checked)
        inquiry = sqlstatement.all()
        if not inquiry:
            raise NoResultFound
        return inquiry
    except NoResultFound:
        message = ""
        if year and month:
            message += f"期間が「{year_month}」、"
        if category:
            message += f"カテゴリが「{category.value}」、"
        if priority:
            message += f"優先度が「{priority.value}」、"
        if is_checked is not None:
            message += f"確認済みが「{is_checked}」、"
        if message:
            message = message[:-1] + "の"
        raise HTTPException(status_code=404,
                            detail=f"{message}問い合わせはありません")
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/inquiries/{id}")
@admin_only()
def edit_inquiry(id: int,
                 param: EditInquiry,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    try:
        priority = param.priority.value if param.priority else None
        is_checked = param.is_checked
        inquiry = db.query(db_model.Inquiry).filter(
            db_model.Inquiry.id == id).one_or_none()
        if not inquiry:
            raise NoResultFound
        # 登録があれば更新
        if priority:
            inquiry.priority = priority
        if is_checked is not None:
            inquiry.is_checked = is_checked
        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)
        return inquiry
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"idが「{id}の問い合わせはありません」")
    except Exception:
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
