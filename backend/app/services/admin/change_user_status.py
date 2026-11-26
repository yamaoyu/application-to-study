from app.domain.user.active_admin_policy import ActiveAdminPolicy, UserStatus
from app.error_codes import ConflictCode, NotFoundCode
from app.exceptions import Conflict, NotFound
from app.models.admin_model import StatusChangeResponse
from app.repositories.user_repository import UserRepository


class ChangeUserStatus:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)

    def execute(self, new_status: UserStatus, username: str) -> StatusChangeResponse:
        user = self.user_repo.get_user(username)
        if not user:
            raise NotFound(code=NotFoundCode.USER_NOT_FOUND)
        # この辺りの条件が複雑になったらドメイン層へ移行する
        admin_count = self.user_repo.count_active_admin_number()
        active_admin_policy = ActiveAdminPolicy(
            current_role=user.role,
            current_status=user.status,
            new_role=user.role,
            new_status=new_status,
            active_admin_count=admin_count,
        )
        if not active_admin_policy.can_change():
            raise Conflict(code=ConflictCode.LAST_ADMIN_USER)
        self.user_repo.change_status(user, new_status)
        self.user_repo.flush()
        return StatusChangeResponse(username=user.username, status=new_status)
