import traceback
from lib.log_conf import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.repositories.todo_repository import TodoRepository
from app.models.todo_model import TodosCreateResponse, UpsertTodoParams
from app.error_codes import BadRequestCode, ValidationErrorCode
from collections.abc import Mapping
from app.domain.todo.exceptions import InvalidTodo, TodoValidationReason
from app.domain.todo.todo import TodoDraft
from app.services.todo.error_mapping import to_todo_bad_request_code


class TodoRegisterService:
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def execute(self, todos: list, username: str) -> TodosCreateResponse:
        success_count = 0
        error_count = 0
        results = []
        for raw_todo in todos:
            try:
                validated_todo = parse_todo_params(raw_todo)
                with self.repo.begin_nested():
                    self.repo.insert_todo(validated_todo.title,
                                          validated_todo.due,
                                          validated_todo.detail, username)
                    self.repo.flush()
                    results.append(build_success_result(validated_todo))
                success_count += 1
            except ValidationError as e:
                error_count += 1
                results.append(build_error_result(
                    raw_todo, convert_field_to_error_code(e)))
            except InvalidTodo as invalid_e:
                error_count += 1
                results.append(build_error_result(
                    raw_todo,
                    to_todo_bad_request_code(TodoValidationReason(invalid_e.reason)))
                )
            except Exception:
                error_count += 1
                logger.error(f"todoの作成に失敗しました\n{traceback.format_exc()}")
                results.append(build_error_result(
                    raw_todo, BadRequestCode.UNEXPECTED_ERROR))

        return TodosCreateResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )


def parse_todo_params(raw_todo: dict) -> TodoDraft:
    todo = UpsertTodoParams.model_validate(raw_todo)
    validated_todo = TodoDraft.create(todo.title,
                                      todo.due,
                                      todo.detail)
    return validated_todo


def convert_field_to_error_code(error: ValidationError) -> ValidationErrorCode:
    """ pydanticのValidationErrorをエラーコードに変換する """
    field_error_mapping = {"title": ValidationErrorCode.INVALID_TODO_TITLE,
                           "detail": ValidationErrorCode.INVALID_TODO_DETAIL,
                           "due": ValidationErrorCode.INVALID_TODO_DUE}
    loc = error.errors()[0].get("loc", [])
    if loc and isinstance(loc[-1], str):
        field = loc[-1]
    else:
        field = "unknown"
    return field_error_mapping.get(field, ValidationErrorCode.INVALID_VALUE)


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
