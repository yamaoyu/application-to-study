from app.domain.user.active_admin_policy import ActiveAdminPolicy, UserRole
from app.error_codes import ConflictCode, NotFoundCode
from app.exceptions import Conflict, NotFound
from app.models.admin_model import RoleChangeResponse
from app.repositories.user_repository import UserRepository


class ChangeUserRole:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)

    def execute(self, new_role: UserRole, username: str) -> RoleChangeResponse:
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        # この辺りの条件が複雑になったらドメイン層へ移行する
        admin_count = self.user_repo.count_active_admin_number()
        active_admin_policy = ActiveAdminPolicy(
            current_role=user.role,
            current_status=user.status,
            new_role=new_role,
            new_status=user.status,
            active_admin_count=admin_count,
        )
        if not active_admin_policy.can_change():
            raise Conflict(code=ConflictCode.LAST_ADMIN_USER)
        self.user_repo.change_role(user, new_role)
        self.user_repo.flush()
        return RoleChangeResponse(username=username, role=new_role)
