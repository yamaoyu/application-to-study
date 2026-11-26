from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPEND = "suspended"


class UserRole(StrEnum):
    ADMIN = "admin"
    GENERAL = "general"


class ActiveAdminPolicy:
    def __init__(
        self,
        current_role: UserRole,
        current_status: UserStatus,
        new_role: UserRole,
        new_status: UserStatus,
        active_admin_count: int,
    ) -> None:
        self.current_role = current_role
        self.current_status = current_status
        self.new_role = new_role
        self.new_status = new_status
        self.active_admin_count = active_admin_count

    def can_change(self) -> bool:
        is_currently_active_admin = (
            self.current_role == UserRole.ADMIN
            and self.current_status == UserStatus.ACTIVE
        )
        remains_active_admin = (
            self.new_role == UserRole.ADMIN and self.new_status == UserStatus.ACTIVE
        )

        if not is_currently_active_admin:
            return True

        if remains_active_admin:
            return True

        return self.active_admin_count > 1
