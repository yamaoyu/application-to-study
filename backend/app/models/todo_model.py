from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date
from typing import Optional


class Todo(BaseModel):
    title: str
    due: date
    detail: Optional[str] = None

    @field_validator("title")
    def check_title_length(cls, title):
        if len(title) > 32:
            raise ValueError("タイトルは32字以下で入力してください")
        return title

    @field_validator("detail")
    def check_detail_length(cls, detail):
        if len(detail) > 200:
            raise ValueError("詳細は200字以下で入力してください")
        return detail


class TodosCreateRequest(BaseModel):
    todos: list[Todo]


class TodosCreateResponse(BaseModel):
    message: str


class TodoIdsRequest(BaseModel):
    ids: list[int]


class TodosGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    todo_id: int
    title: str
    status: bool
    due: date
    detail: Optional[str] = None


class TodosFinishResponse(BaseModel):
    message: str
    titles: str


class TodoEditResponse(BaseModel):
    message: str
    title: str
    due: date
    detail: Optional[str] = None
