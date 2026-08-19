import { apiClient } from "./client";
import {
  UpsertTodoResponse,
  DeleteTodoResponse,
  FinishTodoResponse,
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
      "todos/bulk-create",
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
    return apiClient.patch(
      `todos/update/${id}`,
      params
    )
  };

export const finishTodos = (
  ids: FinishTodoParam
): Promise<AxiosResponse<DeleteTodoResponse>> => {
  return apiClient.patch(
    `todos/bulk-finish`,
    ids
  )
};

export const deleteTodos = (
  ids: DeleteTodoParam
): Promise<AxiosResponse<FinishTodoResponse>> => {
  return apiClient.post(
    `todos/bulk-delete`,
    ids
  );
};
