import traceback
from datetime import datetime
from db.database import get_db
from db import db_model
from lib.check_date import set_date_format
from lib.log_conf import logger
from lib.security import (get_current_user, admin_only, login_required,
                          oauth2_scheme)
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.models.inquiry_model import InquiryForm, ResponseInquiry, GetInquiry


router = APIRouter()


def check_data(category, detail):
    """ 問い合わせフォームのデータに不備がないかを確認する """
    if category not in ("要望", "エラー報告", "その他"):
        raise HTTPException(status_code=400, detail="カテゴリは選択肢から選択してください")
    if len(detail) > 256:
        raise HTTPException(status_code=400, detail="詳細は256文字以内で入力してください")


@router.post("/inquiry", status_code=201, response_model=ResponseInquiry)
@login_required()
def send_inquiry(inquiry_form: InquiryForm,
                 db: Session = Depends(get_db),
                 token: str = Depends(oauth2_scheme)):
    try:
        category = inquiry_form.category.value
        detail = inquiry_form.detail
        date = datetime.today()
        check_data(category, detail)
        fetch_data = db.query(db_model.Inquiry).filter(
            db_model.Inquiry.category == category, db_model.Inquiry.detail == detail).one_or_none()
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


@router.get("/inquiry")
@admin_only()
def get_inquiry(condition: GetInquiry,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    try:
        year = condition.year
        month = condition.month
        if ((year and not month) or (not year and month)):
            raise HTTPException(status_code=400, detail="年と月はセットで入力してください")
        category = condition.category.value if condition.category else None
        priority = condition.priority.value if condition.priority else None
        is_watched = condition.is_watched
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
        if is_watched:
            sqlstatement = sqlstatement.filter(db_model.Inquiry.is_watched == is_watched)
        inquiry = sqlstatement.all()
        if not inquiry:
            raise NoResultFound
        return inquiry
    except NoResultFound:
        message = ""
        if year and month:
            message += f"期間が「{year_month}」、"
        if category:
            message += f"カテゴリが「{category}」、"
        if priority:
            message += f"優先度が「{priority}」、"
        if is_watched is not None:
            message += f"確認済みが「{is_watched}」、"
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
