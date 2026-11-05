export type UserRole = "general" | "admin";

export type LoginResponse = {
  access_token: string;
  token_type: string;
  role: UserRole;
  must_change_password: boolean;
};

export type AuthTokenResponse = LoginResponse;
