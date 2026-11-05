from sqlalchemy.orm import Session

from app.domain.todo.exceptions import (
    InvalidTodo,
    TodoAlreadyFinished,
    TodoValidationReason,
)
from app.domain.todo.todo import Todo, TodoDraft
from app.error_codes import ConflictCode, NotFoundCode
from app.exceptions import Conflict, DomainValidationError, NotFound
from app.models.todo_model import TodoEditResponse, UpsertTodoParams
from app.repositories.todo_repository import TodoRepository
from app.services.todo.error_mapping import to_todo_bad_request_code
from lib.log_conf import logger


class TodoEditService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def execute(
        self, todo_id: int, param: UpsertTodoParams, username: str
    ) -> TodoEditResponse:
        todo_row = self.repo.get_todo(todo_id, username)
        if not todo_row:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)

        try:
            editing_todo = Todo(
                todo_id=todo_id,
                title=todo_row.title,
                due=todo_row.due,
                detail=todo_row.detail,
                status=todo_row.status,
            )

            new_todo = TodoDraft.create(param.title, param.due, param.detail)

            editing_todo.edit(
                title=new_todo.title,
                due=new_todo.due,
                detail=new_todo.detail,
            )
            self.repo.update_todo_content(
                todo_row, new_todo.title, new_todo.due, new_todo.detail
            )
            logger.info(f"{username}がTodoを編集 ID:{todo_id}")
            return TodoEditResponse(
                success_count=1,
                error_count=0,
                results=[self._build_success_result(editing_todo)],
            )
        except InvalidTodo as invalid_e:
            raise DomainValidationError(
                code=to_todo_bad_request_code(TodoValidationReason(invalid_e.reason)),
                field=invalid_e.field,
                detail=invalid_e.detail,
            ) from invalid_e
        except TodoAlreadyFinished as finished_e:
            raise Conflict(code=ConflictCode.TODO_ALREADY_FINISHED) from finished_e

    def _build_success_result(self, todo: Todo) -> dict:
        return {
            "title": todo.title,
            "due": todo.due,
            "detail": todo.detail,
            "result": "success",
            "reason": None,
        }
