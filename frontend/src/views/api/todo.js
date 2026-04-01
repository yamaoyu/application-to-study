import { apiClient } from "./client";

export const postTodos = (todos) => {
  return apiClient.post(
    "todos/multi",
    { todos }
  )
};
