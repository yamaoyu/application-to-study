class ActivityDomainError(Exception):
    pass


class ActivityAlreadyFinished(ActivityDomainError):
    pass
