from pydantic import BaseModel, field_validator


class RegisterIncome(BaseModel):
    salary: float

    @field_validator("salary")
    def check_salary(cls, salary):
        if salary <= 0:
            raise ValueError("給料は正の数を入力して下さい")
        return salary
