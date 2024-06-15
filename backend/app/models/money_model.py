from pydantic import BaseModel


class RegisterIncome(BaseModel):
    year_month: str
    monthly_income: float


class YearMonth(BaseModel):
    year_month: str
