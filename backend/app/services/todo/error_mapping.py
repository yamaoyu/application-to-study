from app.domain.todo.exceptions import TodoValidationReason
from app.error_codes import ValidationErrorCode

TODO_VALIDATION_REASON_TO_ERROR_CODE = {
    TodoValidationReason.TITLE_REQUIRED: ValidationErrorCode.INVALID_TODO_TITLE,
    TodoValidationReason.TITLE_TOO_LONG: ValidationErrorCode.INVALID_TODO_TITLE,
    TodoValidationReason.DUE_REQUIRED: ValidationErrorCode.INVALID_TODO_DUE,
    TodoValidationReason.INVALID_DUE: ValidationErrorCode.INVALID_TODO_DUE,
    TodoValidationReason.DETAIL_TOO_LONG: ValidationErrorCode.INVALID_TODO_DETAIL,
}


def to_todo_bad_request_code(reason: TodoValidationReason) -> ValidationErrorCode:
    return TODO_VALIDATION_REASON_TO_ERROR_CODE[reason]
