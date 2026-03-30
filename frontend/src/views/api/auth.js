import { apiClient } from "./client";

export function verifyRefreshToken(){
    const response = apiClient.post(
      "token",
        {},
        { withCredentials: true })
    return response
};
