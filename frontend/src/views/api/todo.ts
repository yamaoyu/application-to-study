import { apiClient } from "./client";
import {
  UpsertTodoResponse,
  UpsertTodoParam,
  GetTodoResponse,
  GetTodosParam,
  DeleteTodoParam,
  FinishTodoParam
} from "../types/todo";
import type { AxiosResponse } from "axios";

export const postTodos =
  (todos: UpsertTodoParam[]
  ): Promise<AxiosResponse<UpsertTodoResponse>> => {
    return apiClient.post(
      "todos",
      { todos }
    )
  };

export const getTodos = (
  params: GetTodosParam
): Promise<AxiosResponse<GetTodoResponse>> => {
  return apiClient.get("todos", { params }
  );
};

export const editTodo =
  (id: number, params: UpsertTodoParam
  ): Promise<AxiosResponse<UpsertTodoResponse>> => {
    return apiClient.put(
      `todos/update/${id}`,
      params
    )
  };

export const finishTodos = (
  ids: FinishTodoParam
): Promise<AxiosResponse<UpsertTodoResponse>> => {
  return apiClient.put(
    `todos/finish`,
    ids
  )
};

export const deleteTodos = (
  ids: DeleteTodoParam
): Promise<AxiosResponse<UpsertTodoResponse>> => {
  return apiClient.put(
    `todos/delete`,
    ids
  );
};
