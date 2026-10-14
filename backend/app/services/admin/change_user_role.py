from app.repositories.user_repository import UserRepository
from app.error_codes import NotFoundCode, ConflictCode
from app.exceptions import NotFound, Conflict
from app.models.admin_model import RoleChangeResponse, UserRole


class ChangeUserRole:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)

    def execute(self, new_role: UserRole, username: str) -> RoleChangeResponse:
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        # この辺りの条件が複雑になったらドメイン層へ移行する
        admin_count = self.user_repo.count_active_admin_number()
        if self.is_last_admin(new_role, user.status, admin_count):
            raise Conflict(code=ConflictCode.LAST_ADMIN_USER)
        self.user_repo.change_role(user, new_role)
        self.user_repo.flush()
        return RoleChangeResponse(
            username=username,
            role=new_role
        )

    @staticmethod
    def is_last_admin(new_role: UserRole, user_status, admin_count: int) -> bool:
        """ adminロールでactiveなユーザーが0人にならないか確認する """
        if new_role == "admin":
            return False
        if user_status == "suspended":
            return False
        if admin_count > 1:
            return False
        print(new_role, user_status, admin_count)
        return True
