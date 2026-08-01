export type UserRole = "general" | "admin"

export type LoginResponse = {
    access_token: string,
    token_type: string,
    role: UserRole
}

export type AuthTokenResponse = {
    access_token: string;
    token_type: string;
};
