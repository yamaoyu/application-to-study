import { apiClient } from "./client";

export function verifyRefreshToken(){
    const response = apiClient.post(
      "token",
        {},
        { withCredentials: true })
    return response
};

export const login = (username, password) => {
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
