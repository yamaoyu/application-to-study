from fastapi import APIRouter, Depends, HTTPException
from app.models.money_model import RegisterIncome, YearMonth
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session
import re

router = APIRouter()


@router.post("/income", status_code=201)
def register_salary(income: RegisterIncome,
                    db: Session = Depends(get_db)):
    """  月収を登録する """
    monthly_income = income.monthly_income
    year_month = income.year_month
    # year_monthのフォーマットがYYYY-MMか確認
    if not re.match(r"^\d{4}-\d{2}$", year_month):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM")
    if monthly_income < 0:
        raise HTTPException(status_code=400, detail="正の数を入力して下さい")
    data = db_model.Income(year_month=year_month,
                           monthly_income=monthly_income,
                           bonus=0)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
        return {"message": f"{year_month}の月収:{monthly_income}万円"}
    except Exception:
        raise HTTPException(status_code=400, detail="その月の月収は既に登録されています。")


@router.get("/income", status_code=200)
def get_monthly_income(year_month: YearMonth,
                       db: Session = Depends(get_db)):
    """ 月毎の収入を確認する """
    year_month = year_month.year_month
    try:
        result = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month).one()
        total_income = result.monthly_income + result.bonus
        return {"今月の詳細": result, "ボーナス換算後の月収": total_income}
    except Exception:
        raise HTTPException(status_code=400, detail="その月の月収は未登録です。")
