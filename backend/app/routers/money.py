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
from pydantic import ValidationError


router = APIRouter()


@router.post("/incomes/{year}/{month}", status_code=201)
def register_salary(year: int,
                    month: int,
                    income: RegisterIncome,
                    current_user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """  月収を登録する """
    try:
        salary = income.salary
        CheckDate(year=year, month=month)
        year_month = f"{year}-{month}"
        username = current_user['username']
        data = db_model.Income(year_month=year_month,
                               salary=salary,
                               username=username)
        db.add(data)
        db.commit()
        logger.info(f"{username}:{year_month}の月収を登録")
        return {"message": f"{year_month}の月収:{salary}万円"}
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="その月の月収は既に登録されています")
        raise HTTPException(
            status_code=400, detail="データの整合性エラーが発生しました。入力データを確認してください")
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
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
        total_income = round((result.salary + result.total_bonus - result.total_penalty), 2)
        pay_adjustment = round((result.total_bonus - result.total_penalty), 2)
        logger.info(f"{username}:{year_month}の月収を取得")
        return {"month_info": result, "total_income": total_income, "pay_adjustment": pay_adjustment}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"{year_month}の月収は未登録です")
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"月収の取得処理中にエラーが発生しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
