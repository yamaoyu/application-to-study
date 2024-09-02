import traceback
from app.models.money_model import RegisterIncome
from app import set_date_format
from db import db_model
from db.database import get_db
from security import get_current_user
from log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()


@router.post("/income", status_code=201)
def register_salary(income: RegisterIncome,
                    current_user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """  月収を登録する """
    monthly_income = income.monthly_income
    year_month = set_date_format(income.year, income.month)
    username = current_user['username']
    if monthly_income < 0:
        raise HTTPException(status_code=400, detail="正の数を入力して下さい")
    data = db_model.Income(year_month=year_month,
                           monthly_income=monthly_income,
                           bonus=0,
                           username=username)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
        logger.info(f"{username}:{year_month}の月収を登録")
        return {"message": f"{year_month}の月収:{monthly_income}万円"}
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="その月の月収は既に登録されています")
        raise HTTPException(
            status_code=400, detail="Integrity errorが発生しました")
    except Exception:
        logger.warning(f"月収の登録処理中にエラーが発生しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/income/{year}/{month}", status_code=200)
def get_monthly_income(year: str,
                       month: str,
                       current_user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """ 月毎の収入を確認する """
    try:
        year_month = f"{year}-{month}"
        username = current_user['username']
        result = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == username).one()
        total_income = result.monthly_income + result.bonus
        logger.info(f"{username}:{year_month}の月収を取得")
        return {"今月の詳細": result, "ボーナス換算後の月収": total_income}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"{year_month}の月収は未登録です")
    except Exception:
        logger.warning(f"月収の取得処理中にエラーが発生しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
