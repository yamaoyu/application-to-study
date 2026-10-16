export type UserStatus = "active" | "suspended"
export type UserStatusFilter = UserStatus | ""

export type UserRole = "admin" | "general"
export type UserRoleFilter = UserRole | "";

export type UserItem = {
    username: string
    status: UserStatus
    last_active_at: string
    created_at: string
    role: UserRole
}

export type GetUsersResponse = { users: UserItem[] }

export type GetUsersParams = {
    status?: UserStatus
    last_active_at?: string
    created_at?: string
    role?: UserRole
    username?: string
}

export type ChangeRoleParams = {
    username: string
    role: UserRole
}

export type ChangeRoleResponse = ChangeRoleParams

export type ChangeStatusParams = {
    username: string
    status: UserStatus
}

export type ChangeStatusResponse = ChangeRoleParams
