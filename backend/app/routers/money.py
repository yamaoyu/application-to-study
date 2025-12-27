from app.models.money_model import RegisterIncome
from db.database import get_db
from lib.security import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.services.money_service import MoneyService
from app.models.common_model import CheckYearMonth


router = APIRouter()


def get_money_service(db: Session = Depends(get_db)) -> MoneyService:
    return MoneyService(db)


def get_year_month(year: int, month: int) -> CheckYearMonth:
    return CheckYearMonth(year=year, month=month)


@router.post("/incomes/{year}/{month}", status_code=201)
def register_salary(income: RegisterIncome,
                    param: CheckYearMonth = Depends(),
                    current_user: dict = Depends(get_current_user),
                    service: MoneyService = Depends(get_money_service)):
    """  月収を登録する """
    username = current_user["username"]
    return service.register_monthly_salary(param.year, param.month, income.salary, username)


@router.get("/incomes/{year}/{month}", status_code=200)
def get_monthly_income(current_user: dict = Depends(get_current_user),
                       param: CheckYearMonth = Depends(),
                       service: MoneyService = Depends(get_money_service)):
    """ 月毎の収入を確認する """
    username = current_user["username"]
    return service.get_monthly_income(param.year, param.month, username)
