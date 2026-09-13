from pydantic import BaseModel, ConfigDict


class RegisterIncomeRequest(BaseModel):
    salary: float


class RegisterSalaryResponse(BaseModel):
    year: int
    month: int
    salary: float


class GetIncomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    base_income: float
    pay_adjustment: float
    total_bonus: float
    total_penalty: float
