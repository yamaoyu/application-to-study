from sqlalchemy.orm import Session

from app.error_codes import NotFoundCode
from app.exceptions import NotFound
from app.models.todo_model import Todo, TodoGetResponse
from app.repositories.todo_repository import TodoRepository
from lib.log_conf import logger


class TodoQueryService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def get_todo(self, todo_id: int, username: str) -> Todo:
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        logger.info(f"Todoを取得:{username}:ID{todo.todo_id}")
        return Todo.model_validate(todo)

    def get_todos(
        self,
        username: str,
        status: bool | None = None,
        start_due: str | None = None,
        end_due: str | None = None,
        title: str | None = None,
    ) -> TodoGetResponse:
        todos = self.repo.get_todos(
            username=username,
            status=status,
            start_due=start_due,
            end_due=end_due,
            title=title,
        )
        logger.info(f"ユーザー名:{username}  Todoを全て取得")
        if not todos:
            return TodoGetResponse(todos=[])
        # dbから取得したままでは「db.db_model.Todo」なので整形する
        converted_todos = [Todo.model_validate(todo) for todo in todos]
        return TodoGetResponse(todos=converted_todos)
