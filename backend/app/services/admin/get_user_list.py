from datetime import datetime

from app.models.admin_model import GetUsersResponse, UserItem
from app.repositories.user_repository import UserRepository


class GetUserList:
    def __init__(self, db) -> None:
        self.user_repo = UserRepository(db)

    def execute(
        self,
        status: str | None = None,
        last_active_at: datetime | None = None,
        created_at: datetime | None = None,
        role: str | None = None,
        username: str | None = None,
    ) -> GetUsersResponse:
        users = self.user_repo.get_users(
            status, last_active_at, created_at, role, username
        )
        parsed_users = [UserItem.model_validate(user) for user in users]
        return GetUsersResponse(users=parsed_users)
