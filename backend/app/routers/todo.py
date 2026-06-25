from fastapi import APIRouter, Depends
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.todo_model import (Todo,
                                   TodosCreateRequest,
                                   TodoIdsRequest,
                                   TodosCreateResponse,
                                   TodoGetResponse,
                                   TodoEditResponse,
                                   TodosFinishResponse)
from app.dependencies.auth import get_current_user
from typing import Optional
from ..services.todo_service import TodoService


router = APIRouter()


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.post("/todos", status_code=201, response_model=TodosCreateResponse)
def create_todos(params: TodosCreateRequest,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.create_todos(params.todos, username)


@router.get("/todos", status_code=200, response_model=list[TodoGetResponse])
def get_all_todo(status: Optional[bool] = None,
                 start_due: Optional[str] = None,
                 end_due: Optional[str] = None,
                 title: Optional[str] = None,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.get_todos(status, start_due, end_due, title, username)


@router.get("/todos/{todo_id}", status_code=200, response_model=TodoGetResponse)
def get_specific_todo(todo_id: int,
                      service: TodoService = Depends(get_todo_service),
                      current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.get_todo(todo_id, username)


@router.put("/todos/delete", status_code=204)
def delete_todos(params: TodoIdsRequest,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.delete_todos(params, username)


@router.put("/todos/update/{todo_id}", status_code=200, response_model=TodoEditResponse)
def edit_todo(todo_id: int,
              new_todo: Todo,
              service: TodoService = Depends(get_todo_service),
              current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.edit_todo(todo_id, new_todo, username)


@router.put("/todos/finish", status_code=200, response_model=TodosFinishResponse)
def finish_todos(params: TodoIdsRequest,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.finish_todos(params, username)
