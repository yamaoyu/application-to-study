from sqlalchemy.orm import Session
from app.repositories.todo_repository import TodoRepository
from app.models.todo_model import (TodoIdsRequest,
                                   TodosDeleteResponse)
from app.error_codes import NotFoundCode
from typing import Optional


class TodoDeleteService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def execute(self, params: TodoIdsRequest, username: str) -> TodosDeleteResponse:
        requested_ids = params.ids

        # 削除するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, ids=requested_ids)
        todos_by_id = {todo.todo_id: todo for todo in todos}

        results = []
        success_count = 0
        error_count = 0
        existing_ids = set()
        for id in requested_ids:
            current_todo = todos_by_id.get(id, None)
            if not current_todo:
                error_count += 1
                results.append(self._build_error_result(
                    id=id, title=None, reason=NotFoundCode.TODO_NOT_FOUND
                ))
                continue
            existing_ids.add(id)
            success_count += 1
            results.append(self._build_success_result(id=id, title=current_todo.title))
        self.repo.delete_todos(existing_ids, username)
        return TodosDeleteResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )

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
