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
