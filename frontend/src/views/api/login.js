import { apiClient } from "./client";

export const login = (username, password) => {
  return apiClient.post(
    "login",
    { username, password },
    { withCredentials: true }
  )
};
