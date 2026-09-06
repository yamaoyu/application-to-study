from app.domain.todo.exceptions import TodoValidationReason
from app.error_codes import BadRequestCode

TODO_VALIDATION_REASON_TO_ERROR_CODE = {
    TodoValidationReason.TITLE_REQUIRED: BadRequestCode.INVALID_TODO_TITLE,
    TodoValidationReason.TITLE_TOO_LONG: BadRequestCode.INVALID_TODO_TITLE,
    TodoValidationReason.DUE_REQUIRED: BadRequestCode.INVALID_TODO_DUE,
    TodoValidationReason.INVALID_DUE: BadRequestCode.INVALID_TODO_DUE,
    TodoValidationReason.DETAIL_TOO_LONG: BadRequestCode.INVALID_TODO_DETAIL,
}


def to_todo_bad_request_code(reason: TodoValidationReason) -> BadRequestCode:
    return TODO_VALIDATION_REASON_TO_ERROR_CODE[reason]
