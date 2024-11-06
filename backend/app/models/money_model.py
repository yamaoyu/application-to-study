from pydantic import BaseModel


class RegisterIncome(BaseModel):
    year: str
    month: str
    salary: float
