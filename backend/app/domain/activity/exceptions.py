class ActivityDomainError(Exception):
    pass


class ActivityAlreadyFinished(ActivityDomainError):
    pass


class InvalidActivity(ActivityDomainError):
    pass


class ActivityValidationReason(ActivityDomainError):
    INVALID_TARGET_TIME = "INVALID_TARGET_TIME"
    INVALID_ACTUAL_TIME = "INVALID_ACTUAL_TIME"
