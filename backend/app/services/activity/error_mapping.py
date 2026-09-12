from app.domain.activity.exceptions import ActivityValidationReason
from app.error_codes import BadRequestCode

ACTIVITY_VALIDATION_REASON_TO_ERROR_CODE = {
    ActivityValidationReason.INVALID_TARGET_TIME: BadRequestCode.INVALID_TARGET_TIME,
    ActivityValidationReason.INVALID_ACTUAL_TIME: BadRequestCode.INVALID_ACTUAL_TIME,
}


def to_todo_bad_request_code(reason: str) -> BadRequestCode:
    return ACTIVITY_VALIDATION_REASON_TO_ERROR_CODE[reason]
