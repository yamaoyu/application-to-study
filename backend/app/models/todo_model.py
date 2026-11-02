from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_core import PydanticCustomError


class UpsertTodoParams(BaseModel):
    title: str
    due: str
    detail: str | None = None


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
        return ids


class Todo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    todo_id: int
    title: str
    status: bool
    due: date
    detail: str | None = None


class TodoGetResponse(BaseModel):
    # TODO: 将来的にサーバーサイドページングにするときはtotalを追加する
    todos: list[Todo] | list


class TodosFinishResponse(TodoManupulate):
    pass


class TodosDeleteResponse(TodoManupulate):
    pass


class TodoEditResponse(TodoManupulate):
    pass
