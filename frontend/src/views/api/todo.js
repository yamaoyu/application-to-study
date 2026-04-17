import { apiClient } from "./client";

export const postTodos = (todos) => {
  return apiClient.post(
    "todos/multi",
    { todos }
  )
};

export const getTodos = (query) => {
  const url = "todos" + (query ? `?${query}` : "");
  return apiClient.get(url);
};

export const editTodo = (id, params) => {
  return apiClient.put(
    `todos/${id}`,
    params
  )
};

export const finishTodos = (ids) => {
  return apiClient.put(
    `todos/multi/finish`,
    ids
  )
};

export const deleteTodos = (ids) => {
  return apiClient.put(
    `todos/multi/delete`,
    ids
  );
};
