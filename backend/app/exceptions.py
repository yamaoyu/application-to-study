class AppError(Exception):
    """アプリケーション共通例外"""

    def __init__(self, detail: str):
        self.detail = detail


class NotFound(AppError):
    """リソースが存在しない場合の例外"""
    pass


class BadRequest(AppError):
    """不正なリクエストの場合の例外"""
    pass


class Conflict(AppError):
    """リソースの競合が発生した場合の例外"""
    pass


class NotAuthorized(AppError):
    """認証失敗、認証されていない場合の例外"""
    pass


class Forbidden(AppError):
    """認可されていない場合の例外"""
    pass


class BulkOperationFailed(AppError):
    """活動記録などが複数送られた場合の例外"""

    def __init__(self, results: list, detail: str = "処理に失敗しました"):
        self.results = results
        self.detail = detail
