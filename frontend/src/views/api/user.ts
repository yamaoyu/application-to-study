import { apiClient } from './client';

export const createUser = (
  username: string, password: string, email: string) => {
  return apiClient.post(
    "users",
    {
      username,
      password,
      email
    }
  )
};

export const updatePassword = (oldPassword: string, newPassword: string) => {
  return apiClient.put(
    "password",
    {
      old_password: oldPassword,
      new_password: newPassword
    }
  )
};
