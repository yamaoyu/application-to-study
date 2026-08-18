from fastapi import APIRouter, Depends
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.todo_model import (Todo,
                                   UpsertTodoParams,
                                   TodosCreateRequest,
                                   TodoIdsRequest,
                                   TodosCreateResponse,
                                   TodoGetResponse,
                                   TodoEditResponse,
                                   TodosDeleteResponse,
                                   TodosFinishResponse)
from app.dependencies.auth import get_current_user
from typing import Optional
from ..services.todo_service import TodoService


router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.post("/bulk-create", status_code=200, response_model=TodosCreateResponse)
def create_todos(params: TodosCreateRequest,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.create_todos(params.todos, username)


@router.get("", status_code=200, response_model=TodoGetResponse)
def get_all_todo(status: Optional[bool] = None,
                 start_due: Optional[str] = None,
                 end_due: Optional[str] = None,
                 title: Optional[str] = None,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.get_todos(status, start_due, end_due, title, username)


@router.get("/{todo_id}", status_code=200, response_model=Todo)
def get_specific_todo(todo_id: int,
                      service: TodoService = Depends(get_todo_service),
                      current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.get_todo(todo_id, username)


@router.post("/bulk-delete", status_code=200, response_model=TodosDeleteResponse)
def delete_todos(params: TodoIdsRequest,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.delete_todos(params, username)


@router.patch("/update/{todo_id}", status_code=200, response_model=TodoEditResponse)
def edit_todo(todo_id: int,
              new_todo: UpsertTodoParams,
              service: TodoService = Depends(get_todo_service),
              current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.edit_todo(todo_id, new_todo, username)


@router.patch("/bulk-finish", status_code=200, response_model=TodosFinishResponse)
def finish_todos(params: TodoIdsRequest,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.finish_todos(params, username)
