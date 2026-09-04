from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.repositories.todo_repository import TodoRepository
from app.models.todo_model import (TodoIdsRequest,
                                   TodosFinishResponse)
from app.error_codes import NotFoundCode, ConflictCode
from typing import Optional
from app.domain.todo.todo import Todo
from app.domain.todo.exceptions import TodoAlreadyFinished


class TodoFinishService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def execute(self, params: TodoIdsRequest, username: str) -> TodosFinishResponse:
        requested_ids = params.ids
        todos = self.repo.get_todos(username=username, ids=requested_ids)
        todos_by_id = {todo.todo_id: todo for todo in todos}

        results = []
        success_count = 0
        error_count = 0
        existing_ids = set()
        for id in requested_ids:
            todo_row = todos_by_id.get(id, None)
            if not todo_row:
                error_count += 1
                results.append(self._build_error_result(
                    id=id, title=None, reason=NotFoundCode.TODO_NOT_FOUND
                ))
                continue
            todo = Todo(todo_id=todo_row.todo_id,
                        title=todo_row.title,
                        detail=todo_row.detail,
                        due=todo_row.due,
                        status=todo_row.status)
            try:
                todo.finish()
                existing_ids.add(id)
                success_count += 1
                results.append(self._build_success_result(id=id, title=todo_row.title))
            except TodoAlreadyFinished:
                error_count += 1
                results.append(self._build_error_result(
                    todo.todo_id, todo.title, ConflictCode.TODO_ALREADY_FINISHED))

        self.repo.finish_todos(existing_ids, username)
        logger.info(f"{username}が複数のTodoを完了 IDs:{requested_ids}")
        return TodosFinishResponse(
            success_count=success_count,
            error_count=error_count,
            results=results)

    def _build_error_result(self, id: int, title: Optional[str], reason: str) -> dict:
        return {
            "todo_id": id,
            "title": title,
            "result": "error",
            "reason": reason
        }

    def _build_success_result(self, id: int, title: str) -> dict:
        return {
            "todo_id": id,
            "title": title,
            "result": "success",
            "reason": None
        }
