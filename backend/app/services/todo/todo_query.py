from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.repositories.todo_repository import TodoRepository
from typing import Optional
from app.exceptions import NotFound
from app.error_codes import NotFoundCode
from app.models.todo_model import (Todo,
                                   TodoGetResponse)


class TodoQueryService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def get_todo(self, todo_id: int, username: str) -> Todo:
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        logger.info(f"Todoを取得:{username}:ID{todo.todo_id}")
        return Todo.model_validate(todo)

    def get_todos(self,
                  status: Optional[bool],
                  start_due: Optional[str],
                  end_due: Optional[str],
                  title: Optional[str],
                  username: str) -> TodoGetResponse:
        todos = self.repo.get_todos(username=username, status=status,
                                    start_due=start_due, end_due=end_due, title=title)
        logger.info(f"ユーザー名:{username}  Todoを全て取得")
        if not todos:
            return TodoGetResponse(todos=[])
        # dbから取得したままでは「db.db_model.Todo」なので整形する
        converted_todos = [Todo.model_validate(todo) for todo in todos]
        return TodoGetResponse(todos=converted_todos)
