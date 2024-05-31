from pydantic import BaseModel


class TimeIn(BaseModel):
    hour: int


class RegisterSalary(BaseModel):
    salary: int
