import { apiClient } from './client';

export const createUser = (param) => {
  return apiClient.post(
    "users",
    { 
      username: param.username, 
      password: param.password,
      email: param.email }
  )
};

export const updatePassword = (oldPassword, newPassword) => {
  return apiClient.put(
    "password",
    {
      old_password: oldPassword,
      new_password: newPassword
    }
  )
};
