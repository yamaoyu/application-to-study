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
