from app.repositories.user_repository import UserRepository
from app.error_codes import NotFoundCode, ConflictCode
from app.exceptions import NotFound, Conflict
from app.models.admin_model import StatusChangeResponse, UserStatus


class ChangeUserStatus:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)

    def execute(self, new_status: UserStatus, username: str) -> StatusChangeResponse:
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        # この辺りの条件が複雑になったらドメイン層へ移行する
        admin_count = self.user_repo.count_active_admin_number()
        if self.is_last_admin(user.role, new_status, admin_count):
            raise Conflict(code=ConflictCode.LAST_ADMIN_USER)
        self.user_repo.change_status(user, new_status)
        self.user_repo.flush()
        return StatusChangeResponse(
            username=user.username,
            status=new_status
        )

    @staticmethod
    def is_last_admin(user_role, new_status, admin_count: int) -> bool:
        """ adminロールでactiveなユーザーが0人にならないか確認する """
        if user_role == "general":
            return False
        if new_status == "active":
            return False
        if admin_count > 1:
            return False
        print(user_role, new_status, admin_count)
        return True
