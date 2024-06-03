from fastapi import APIRouter, Depends, HTTPException
from app.models.money_model import RegisterSalary, YearMonth
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/income", status_code=201)
async def register_salary(salary: RegisterSalary,
                          db: Session = Depends(get_db)):
    income = salary.monthly_income
    year_month = salary.year_month
    data = db_model.Salary(year_month=year_month, monthly_income=income,
                           bonus=0, add_monthly_income=income)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
        return income
    except Exception:
        raise HTTPException(status_code=400, detail="その月の月収は既に登録されています。")


@router.get("/income", status_code=200)
async def get_monthly_income(year_month: YearMonth,
                             db: Session = Depends(get_db)):
    year_month = year_month.year_month
    try:
        result = db.query(db_model.Salary).filter(
            db_model.Salary.year_month == year_month).one()
        total_income = result.monthly_income + result.bonus
        return {"今月の詳細": result, "ボーナス換算後の月収": total_income}
    except Exception:
        raise HTTPException(status_code=400, detail="その月の月収は未登録です。")
