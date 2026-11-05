from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.models.todo_model import (
    Todo,
    TodoEditResponse,
    TodoGetResponse,
    TodoIdsRequest,
    TodosCreateRequest,
    TodosCreateResponse,
    TodosDeleteResponse,
    TodosFinishResponse,
    UpsertTodoParams,
)
from app.services.todo.delete_todo import TodoDeleteService
from app.services.todo.edit_todo import TodoEditService
from app.services.todo.finish_todo import TodoFinishService
from app.services.todo.register_todo import TodoRegisterService
from app.services.todo.todo_query import TodoQueryService
from db.database import get_db

router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_register_service(
    db: Annotated[Session, Depends(get_db)],
) -> TodoRegisterService:
    return TodoRegisterService(db)


def get_todo_edit_service(db: Annotated[Session, Depends(get_db)]) -> TodoEditService:
    return TodoEditService(db)


def get_todo_finish_service(
    db: Annotated[Session, Depends(get_db)],
) -> TodoFinishService:
    return TodoFinishService(db)


def get_todo_delete_service(
    db: Annotated[Session, Depends(get_db)],
) -> TodoDeleteService:
    return TodoDeleteService(db)


def get_todo_query_service(db: Annotated[Session, Depends(get_db)]) -> TodoQueryService:
    return TodoQueryService(db)


@router.post("/bulk-create", status_code=200, response_model=TodosCreateResponse)
def create_todos(
    params: TodosCreateRequest,
    service: Annotated[TodoRegisterService, Depends(get_todo_register_service)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    username = current_user["username"]
    return service.execute(params.todos, username)


@router.get("", status_code=200, response_model=TodoGetResponse)
def get_all_todo(
    service: Annotated[TodoQueryService, Depends(get_todo_query_service)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
    status: bool | None = None,
    start_due: str | None = None,
    end_due: str | None = None,
    title: str | None = None,
):
    username = current_user["username"]
    return service.get_todos(username, status, start_due, end_due, title)


@router.get("/{todo_id}", status_code=200, response_model=Todo)
def get_specific_todo(
    todo_id: int,
    service: Annotated[TodoQueryService, Depends(get_todo_query_service)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    username = current_user["username"]
    return service.get_todo(todo_id, username)


@router.post("/bulk-delete", status_code=200, response_model=TodosDeleteResponse)
def delete_todos(
    params: TodoIdsRequest,
    service: Annotated[TodoDeleteService, Depends(get_todo_delete_service)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    username = current_user["username"]
    return service.execute(params, username)


@router.patch("/update/{todo_id}", status_code=200, response_model=TodoEditResponse)
def edit_todo(
    todo_id: int,
    new_todo: UpsertTodoParams,
    service: Annotated[TodoEditService, Depends(get_todo_edit_service)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    username = current_user["username"]
    return service.execute(todo_id, new_todo, username)


@router.patch("/bulk-finish", status_code=200, response_model=TodosFinishResponse)
def finish_todos(
    params: TodoIdsRequest,
    service: Annotated[TodoFinishService, Depends(get_todo_finish_service)],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    username = current_user["username"]
    return service.execute(params, username)
