from pydantic import BaseModel, field_validator, ConfigDict


class RegisterIncomeRequest(BaseModel):
    salary: float

    @field_validator("salary")
    def check_salary(cls, salary):
        if salary < 5:
            raise ValueError("給料は5以上を入力して下さい")
        elif salary > 2000:
            raise ValueError("給料は2000以下を入力して下さい")
        return salary


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
