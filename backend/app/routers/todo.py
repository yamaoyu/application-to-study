from fastapi import APIRouter, Depends
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.todo_model import Todo, Todos, IDList
from lib.security import get_current_user
from typing import Optional
from ..services.todo_service import TodoService


router = APIRouter()


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.post("/todos", status_code=201)
def create_todo(todo: Todo,
                service: TodoService = Depends(get_todo_service),
                current_user: dict = Depends(get_current_user)):
    username = current_user['username']
    return service.create_todo(todo, username)


@router.post("/todos/multi", status_code=201)
def create_multi_todos(params: Todos,
                       service: TodoService = Depends(get_todo_service),
                       current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.create_todos(params, username)


@router.get("/todos", status_code=200)
def get_all_todo(status: Optional[bool] = None,
                 start_due: Optional[str] = None,
                 end_due: Optional[str] = None,
                 title: Optional[str] = None,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.get_todos(status, start_due, end_due, title, username)


@router.get("/todos/{todo_id}", status_code=200)
def get_specific_todo(todo_id: int,
                      service: TodoService = Depends(get_todo_service),
                      current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.get_todo(todo_id, username)


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int,
                service: TodoService = Depends(get_todo_service),
                current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.delete_todo(todo_id, username)


@router.put("/todos/multi/delete", status_code=204)
def delete_todos(params: IDList,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.delete_todos(params, username)


@router.put("/todos/{todo_id}", status_code=200)
def edit_todo(todo_id: int,
              new_todo: Todo,
              service: TodoService = Depends(get_todo_service),
              current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.edit_todo(todo_id, new_todo, username)


@router.put("/todos/finish/{todo_id}", status_code=200)
def finish_todo(todo_id: int,
                service: TodoService = Depends(get_todo_service),
                current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.finish_todo(todo_id, username)


@router.put("/todos/multi/finish", status_code=200)
def finish_todos(params: IDList,
                 service: TodoService = Depends(get_todo_service),
                 current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return service.finish_todos(params, username)
