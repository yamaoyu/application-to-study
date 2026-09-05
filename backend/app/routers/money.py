from app.models.money_model import RegisterIncomeRequest, RegisterSalaryResponse, GetIncomeResponse
from db.database import get_db
from app.dependencies.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.services.money.register_monthly_salary import RegisterSalaryUsecase
from app.services.money.get_monthly_income import GetMonthlyIncomeUsecase
from app.models.common_model import CheckYearMonth


router = APIRouter(prefix="/incomes", tags=["incomes"])


def get_register_salary_service(db: Session = Depends(get_db)) -> RegisterSalaryUsecase:
    return RegisterSalaryUsecase(db)


def get_fetch_monthly_income_service(db: Session = Depends(get_db)) -> GetMonthlyIncomeUsecase:
    return GetMonthlyIncomeUsecase(db)


def get_year_month(year: int, month: int) -> CheckYearMonth:
    return CheckYearMonth(year=year, month=month)


@router.post("/{year}/{month}", status_code=201, response_model=RegisterSalaryResponse)
def register_salary(income: RegisterIncomeRequest,
                    param: CheckYearMonth = Depends(),
                    current_user: dict = Depends(get_current_user),
                    service: RegisterSalaryUsecase = Depends(get_register_salary_service)):
    """  月収を登録する """
    username = current_user["username"]
    return service.execute(param.year, param.month, income.salary, username)


@router.get("/{year}/{month}", status_code=200, response_model=GetIncomeResponse)
def get_monthly_income(current_user: dict = Depends(get_current_user),
                       param: CheckYearMonth = Depends(),
                       service: GetMonthlyIncomeUsecase = Depends(get_fetch_monthly_income_service)):
    """ 月毎の収入を確認する """
    username = current_user["username"]
    return service.execute(param.year, param.month, username)
