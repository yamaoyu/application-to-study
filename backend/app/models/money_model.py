from pydantic import BaseModel


class RegisterSalary(BaseModel):
    year_month: str
    monthly_income: int


class YearMonth(BaseModel):
    year_month: str
