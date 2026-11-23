from pydantic import BaseModel, ConfigDict

from app.models.types.money_serializer import Money


class RegisterIncomeRequest(BaseModel):
    salary: Money


class RegisterSalaryResponse(BaseModel):
    year: int
    month: int
    salary: Money


class GetIncomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    base_income: Money
    pay_adjustment: Money
    total_bonus: Money
    total_penalty: Money
