from app.models.money_model import RegisterIncome
from db.database import get_db
from lib.security import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.services.money_service import MoneyService


router = APIRouter()


def get_money_service(db: Session = Depends(get_db)) -> MoneyService:
    return MoneyService(db)


@router.post("/incomes/{year}/{month}", status_code=201)
def register_salary(year: int,
                    month: int,
                    income: RegisterIncome,
                    current_user: dict = Depends(get_current_user),
                    service: MoneyService = Depends(get_money_service)):
    """  月収を登録する """
    username = current_user["username"]
    return service.register_monthly_salary(year, month, income.salary, username)


@router.get("/incomes/{year}/{month}", status_code=200)
def get_monthly_income(year: int,
                       month: int,
                       current_user: dict = Depends(get_current_user),
                       service: MoneyService = Depends(get_money_service)):
    """ 月毎の収入を確認する """
    username = current_user["username"]
    return service.get_monthly_income(year, month, username)
