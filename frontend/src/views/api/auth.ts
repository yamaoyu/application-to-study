import { apiClient } from "./client";
import type { AxiosResponse } from "axios";
import { AuthTokenResponse, LoginResponse } from "../types/auth";

export function verifyRefreshToken(): Promise<AxiosResponse<AuthTokenResponse>> {
  const response = apiClient.post(
    "token",
    {},
    { withCredentials: true })
  return response
};

export const login = (
  username: string, password: string
): Promise<AxiosResponse<LoginResponse>> => {
  return apiClient.post(
    "login",
    { username, password },
    { withCredentials: true }
  )
};

export const logout = () => {
  return apiClient.post(
    "logout",
    {},
    { withCredentials: true }
  )
};
