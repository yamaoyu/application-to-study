export type UserStatus = "active" | "suepended"
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
