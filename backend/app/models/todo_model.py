from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date
from typing import Optional
from pydantic_core import PydanticCustomError


class UpsertTodoParams(BaseModel):
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
        if detail is None:
            return detail
        if len(detail) > 200:
            raise ValueError("詳細は200字以下で入力してください")
        return detail


class TodosCreateRequest(BaseModel):
    todos: list

    @field_validator("todos")
    def validate_todos(cls, todos):
        if not todos:
            raise ValueError("登録するTodoが送られていません")

        return todos


class TodoManupulate(BaseModel):
    success_count: int
    error_count: int
    results: list


class TodosCreateResponse(TodoManupulate):
    pass


class TodoIdsRequest(BaseModel):
    ids: list[int]

    @field_validator("ids")
    def remove_duplicates(cls, ids):
        if not ids:
            raise PydanticCustomError(
                "empty_list",
                "idsは1件以上指定してください",
            )
        return list(dict.fromkeys(ids))


class Todo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    todo_id: int
    title: str
    status: bool
    due: date
    detail: Optional[str] = None


class TodoGetResponse(BaseModel):
    # TODO: 将来的にサーバーサイドページングにするときはtotalを追加する
    todos: list[Todo] | list


class TodosFinishResponse(TodoManupulate):
    pass


class TodosDeleteResponse(TodoManupulate):
    pass


class TodoEditResponse(TodoManupulate):
    pass
