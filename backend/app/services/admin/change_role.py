from app.repositories.user_repository import UserRepository
from app.error_codes import NotFoundCode, ConflictCode
from app.exceptions import NotFound, Conflict
from app.models.admin_model import RoleChangeResponse, UserRole


class ChangeUserRole:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)

    def execute(self, role: UserRole, username: str) -> RoleChangeResponse:
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        # この辺りの条件が複雑になったらドメイン層へ移行する
        admin_count = self.user_repo.count_active_admin_number()
        if user.role == "admin" and admin_count <= 1:
            raise Conflict(code=ConflictCode.LAST_ADMIN_USER)
        self.user_repo.change_role(user, role)
        self.user_repo.flush()
        return RoleChangeResponse(
            username=username,
            role=role
        )
