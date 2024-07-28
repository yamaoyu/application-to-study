import re
from logging import getLogger, basicConfig, INFO
from app.models.money_model import RegisterIncome
from db import db_model
from db.database import get_db
from security import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

basicConfig(level=INFO, format="%(levelname)s: %(message)s")
logger = getLogger(__name__)

year_month_pattern = r"^\d{4}-\d{2}$"


@router.post("/income", status_code=201)
def register_salary(income: RegisterIncome,
                    current_user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """  月収を登録する """
    monthly_income = income.monthly_income
    year_month = income.year_month
    username = current_user['username']
    # year_monthのフォーマットがYYYY-MMか確認
    if not re.match(year_month_pattern, year_month):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM")
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
        logger.info(f"{username}が{year_month}の月収を登録")
        return {"message": f"{year_month}の月収:{monthly_income}万円"}
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="その月の月収は既に登録されています。")
        raise HTTPException(
            status_code=400, detail="Integrity errorが発生しました")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"月収の登録処理中にエラーが発生しました\n{e}")


@router.get("/income/{year_month}", status_code=200)
def get_monthly_income(year_month: str,
                       current_user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """ 月毎の収入を確認する """
    try:
        username = current_user['username']
        result = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == username).one()
        total_income = result.monthly_income + result.bonus
        logger.info(f"{username}が{year_month}の月収を取得")
        return {"今月の詳細": result, "ボーナス換算後の月収": total_income}
    except NoResultFound:
        raise HTTPException(status_code=400, detail="その月の月収は未登録です。")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"月収の取得処理中にエラーがしました\n{e}")
