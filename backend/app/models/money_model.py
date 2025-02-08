from pydantic import BaseModel, field_validator


class RegisterIncome(BaseModel):
    salary: float

    @field_validator("salary")
    def check_salary(cls, salary):
        if salary < 5:
            raise ValueError("給料は5以上を入力して下さい")
        elif salary > 999:
            raise ValueError("給料は999以下を入力して下さい")
        return salary
