import traceback
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.repositories.todo_repository import TodoRepository
from app.models.todo_model import TodosCreateResponse
from app.error_codes import BadRequestCode
from collections.abc import Mapping
from app.domain.todo.exceptions import InvalidTodo
from app.domain.todo.todo import TodoDraft


class TodoRegisterService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def execute(self, todos: list, username: str) -> TodosCreateResponse:
        success_count = 0
        error_count = 0
        results = []
        for todo in todos:
            try:
                validated_todo = TodoDraft.create(todo.get("title", ""),
                                                  todo.get("due", ""),
                                                  todo.get("detail", ""))
                with self.repo.begin_nested():
                    self.repo.insert_todo(validated_todo.title,
                                          validated_todo.due,
                                          validated_todo.detail, username)
                    self.repo.flush()
                    results.append(build_success_result(validated_todo))
                success_count += 1
            except InvalidTodo as invalid_e:
                error_count += 1
                results.append(build_error_result(todo, invalid_e.reason))
            except Exception:
                error_count += 1
                logger.error(f"todoの作成に失敗しました\n{traceback.format_exc()}")
                results.append(build_error_result(
                    todo, BadRequestCode.UNEXPECTED_ERROR))

        return TodosCreateResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )


def build_success_result(todo):
    return {
        "title": todo.title,
        "due": todo.due,
        "detail": todo.detail,
        "result": "success",
        "reason": None,
    }


def build_error_result(todo, reason):
    """ todo作成時にバリデーションエラー発生時のレスポンス作成 """
    if isinstance(todo, Mapping):
        return {
            "title": todo.get("title", ""),
            "due": todo.get("due", ""),
            "detail": todo.get("detail", ""),
            "result": "error",
            "reason": reason,
        }

    return {
        "title": "",
        "due": "",
        "detail": "",
        "input": repr(todo),
        "result": "error",
        "reason": reason,
    }
