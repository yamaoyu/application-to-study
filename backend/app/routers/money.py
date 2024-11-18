import traceback
from app.models.money_model import RegisterIncome
from app.models.common_model import CheckDate
from db import db_model
from db.database import get_db
from lib.security import get_current_user
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()


@router.post("/incomes/{year}/{month}", status_code=201)
def register_salary(year: int,
                    month: int,
                    income: RegisterIncome,
                    current_user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """  月収を登録する """
    salary = income.salary
    CheckDate(year=year, month=month)
    year_month = f"{year}-{month}"
    username = current_user['username']
    if salary <= 0:
        raise HTTPException(status_code=400, detail="正の数を入力して下さい")
    data = db_model.Income(year_month=year_month,
                           salary=salary,
                           bonus=0,
                           username=username)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
        logger.info(f"{username}:{year_month}の月収を登録")
        return {"message": f"{year_month}の月収:{salary}万円"}
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="その月の月収は既に登録されています")
        raise HTTPException(
            status_code=400, detail="データの整合性エラーが発生しました。入力データを確認してください")
    except Exception:
        logger.error(f"月収の登録処理中にエラーが発生しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/incomes/{year}/{month}", status_code=200)
def get_monthly_income(year: int,
                       month: int,
                       current_user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """ 月毎の収入を確認する """
    try:
        CheckDate(year=year, month=month)
        year_month = f"{year}-{month}"
        username = current_user['username']
        result = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == username).one()
        total_income = result.salary + result.bonus
        logger.info(f"{username}:{year_month}の月収を取得")
        return {"今月の詳細": result, "ボーナス換算後の月収": total_income}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"{year_month}の月収は未登録です")
    except Exception:
        logger.error(f"月収の取得処理中にエラーが発生しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
