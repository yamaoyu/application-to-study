export type UserRole = "general" | "role"

export type LoginResponse = {
    access_token: string,
    token_type: string,
    role: UserRole
}

export type AuthTokenResponse = {
    access_token: string;
    token_type: string;
};
