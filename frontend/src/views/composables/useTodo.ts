import { ref, type Ref } from "vue";
import { postTodos, getTodos, editTodo, finishTodos, deleteTodos } from "../api/todo";
import { parseError } from "../utils/error";
import {
  TodoResult,
  UpsertTodoParam,
  GetTodoResponse,
  TodoInfo
} from "../types/todo";

const errorMessageMap = {
  TODO_NOT_FOUND: (title: string, action: string) => `【Todo${action}失敗】${title}: 登録されていません`,
  TODO_ALREADY_FINISHED: (title: string, action: string) => `【Todo${action}失敗】${title}: 終了したアクションは更新できません`,
  UNEXPECTED_ERROR: (title: string, action: string) => `【Todo${action}失敗】${title}: ${action}に失敗しました`,
};

const makeMessage = (results: TodoResult[], action: string) => {
  let messages = [];

  for (const r of results) {
    if (r.result === "success") {
      messages.push(`【Todo${action}成功】: ${r.title}`)
      continue;
    } else {
      const messageFn = errorMessageMap[r.reason] || errorMessageMap.UNEXPECTED_ERROR;
      messages.push(messageFn(r.title, action));
      continue;
    }
  }
  return messages.join("\n");
};

export const useRegisterTodos = () => {
  const todos = ref<UpsertTodoParam[]>([]);
  const message = ref<string>("");
  const statusCode = ref<number | null>(null);

  const regitserTodos = async () => {
    try {
      const res = await postTodos(todos.value);
      if (res.status === 201) {
        statusCode.value = res.status;
        message.value = makeMessage(res.data.results, "作成");
        todos.value = [];
      }
    } catch (error) {
      statusCode.value = null;
      message.value = parseError(error, "Todoの登録に失敗しました");
    }
  }

  return {
    todos,
    message,
    statusCode,
    regitserTodos
  }
};

export const useGetTodos = (todoMsg: Ref<string>) => {
  const todos = ref<GetTodoResponse[]>([]);
  const statusFilter = ref<string>();
  const startDue = ref<string>();
  const endDue = ref<string>();
  const title = ref<string>();

  const makeParams = () => ({
    status: statusFilter.value || undefined,
    start_due: startDue.value || undefined,
    end_due: endDue.value || undefined,
    title: title.value || undefined,
  });

  const fetchTodos = async () => {
    try {
      const res = await getTodos(makeParams());
      if (res.status === 200) {
        todos.value = res.data;
      }
    } catch (error) {
      todoMsg.value = parseError(error, "Todoの取得に失敗しました");
      todos.value = [];
    }
  }
  return {
    todos,
    statusFilter,
    startDue,
    endDue,
    title,
    fetchTodos
  }
};

type OnSuccess = () => void | Promise<void>;

export const useTodoOperations = (todoMsg: Ref<string>) => {
  const selectedTodoIDs = ref<number[]>([]); // 一括操作するtodoのIDを保持
  const newTodoTitle = ref<string>("");
  const newTodoDetail = ref<string>("");
  const newTodoDue = ref<string>("");

  const updateTodo = async (id: number, onSuccess?: OnSuccess) => {
    try {
      const params = {
        title: newTodoTitle.value,
        detail: newTodoDetail.value,
        due: newTodoDue.value
      };
      const res = await editTodo(id, params);
      if (res.status === 200) {
        todoMsg.value = makeMessage(res.data.results, "更新");
        if (onSuccess) {
          await onSuccess();
        }
      }
    } catch (error) {
      todoMsg.value = parseError(error, "Todoの更新に失敗しました");
    }
  };

  const completeTodos = async (onSuccess?: OnSuccess) => {
    try {
      const params = { "ids": selectedTodoIDs.value }
      const res = await finishTodos(params);
      if (res.status === 200) {
        todoMsg.value = `${res.data.success_count}件のTodoを終了しました\n`;
        todoMsg.value += makeMessage(res.data.results, "終了");
        if (res.data.error_count > 0) {
          todoMsg.value += "\n一部/全てのTodoの終了に失敗しました";
        }
        if (onSuccess) {
          await onSuccess();
        }
      }
    } catch (error) {
      todoMsg.value = parseError(error, "Todoの終了に失敗しました");
    }
  };

  const removeTodos = async (onSuccess?: OnSuccess) => {
    try {
      const params = { "ids": selectedTodoIDs.value };
      const res = await deleteTodos(params);
      if (res.status === 200) {
        todoMsg.value = `${res.data.success_count}件のTodoを削除しました\n`;
        todoMsg.value += makeMessage(res.data.results, "削除");
        if (res.data.error_count > 0) {
          todoMsg.value += "\n一部/全てのTodoの削除に失敗しました";
        }
        if (onSuccess) {
          await onSuccess();
        }
      }
    } catch (error) {
      todoMsg.value = parseError(error, "Todoの削除に失敗しました");
    }
  };

  return {
    selectedTodoIDs,
    newTodoTitle,
    newTodoDetail,
    newTodoDue,
    updateTodo,
    completeTodos,
    removeTodos
  };
};

export type SortTodoType = "id" | "due"

export const useSortTodos = (todos: Ref<TodoInfo[]>) => {
  const sortType = ref("id"); // todoの一覧で表示されるソート順で初期値は登録順(id)
  const sortTodos = async (type: SortTodoType) => {
    sortType.value = type;
    if (sortType.value === "id") {
      todos.value.sort((item1: TodoInfo, item2: TodoInfo) => item1.todo_id - item2.todo_id);
    } else {
      todos.value.sort((item1: TodoInfo, item2: TodoInfo) => {
        if (item1.due > item2.due) return 1;
        if (item1.due < item2.due) return -1;
        return 0;
      });
    }
  };

  return {
    sortType,
    sortTodos
  };
};
