from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.repositories.todo_repository import TodoRepository
from app.models.todo_model import (UpsertTodoParams,
                                   TodoEditResponse)
from app.exceptions import NotFound, Conflict
from app.error_codes import NotFoundCode, ConflictCode
from app.domain.todo.todo import Todo
from app.domain.todo.exceptions import TodoAlreadyFinished


class TodoEditService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def execute(self, todo_id: int, param: UpsertTodoParams, username: str) -> TodoEditResponse:
        todo_row = self.repo.get_todo(todo_id, username)
        if not todo_row:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)

        try:
            new_todo = Todo(
                todo_id=todo_id,
                title=todo_row.title,
                due=todo_row.due,
                detail=todo_row.detail,
                status=todo_row.status,
            )

            new_todo.edit(
                title=param.title,
                due=param.due,
                detail=param.detail,
            )
            self.repo.update_todo_content(todo_row,
                                          param.title,
                                          param.due,
                                          param.detail)
            logger.info(f"{username}がTodoを編集 ID:{todo_id}")
            return TodoEditResponse(
                success_count=1,
                error_count=0,
                results=[self._build_success_result(new_todo)]
            )
        except TodoAlreadyFinished:
            raise Conflict(code=ConflictCode.TODO_ALREADY_FINISHED)

    def _build_success_result(self, todo: Todo) -> dict:
        return {
            "title": todo.title,
            "due": todo.due,
            "detail": todo.detail,
            "result": "success",
            "reason": None,
        }
