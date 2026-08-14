import { ref, type Ref } from "vue";
import { postTodos, getTodos, editTodo, finishTodos, deleteTodos } from "../api/todo";
import { parseError } from "../utils/error";
import {
  TodoUpsertResult,
  TodoDeleteFinishResult,
  UpsertTodoParam,
  TodoInfo
} from "../types/todo";

const errorMessageMap = {
  TODO_NOT_FOUND: (title: string, action: string) => `【Todo${action}失敗】${title}: 登録されていません`,
  TODO_ALREADY_FINISHED: (title: string, action: string) => `【Todo${action}失敗】${title}: 終了したアクションは更新できません`,
  UNEXPECTED_ERROR: (title: string, action: string) => `【Todo${action}失敗】${title}: ${action}に失敗しました`,
};

const makeMessage = (results: TodoUpsertResult[] | TodoDeleteFinishResult[], action: string) => {
  const messages = [];
  for (const r of results) {
    if (r.result === "success") {
      messages.push(`【Todo${action}成功】: ${r.title}`)
      continue;
    }
    // titleがない=DBに対象が見つからなかった場合(TODO_NOT_FOUND)
    if (r.title === null) {
      messages.push(`【Todo${action}失敗】${action}対象が見つかりません`);
      continue;
    }
    // その他のエラー
    const messageFn = errorMessageMap[r.reason] || errorMessageMap.UNEXPECTED_ERROR;
    messages.push(messageFn(r.title, action));
  }
  return messages.join("\n");
};

const makeSummaryMessage = (
  action: string,
  success_count: number,
  error_count: number) => {
  // bulk登録時のリクエスト成功数と失敗数をまとめる
  return `Todo${action}成功: ${success_count}件、失敗:${error_count}件\n`
}

export const useRegisterTodos = () => {
  const todos = ref<UpsertTodoParam[]>([]);
  const message = ref<string>("");
  const statusCode = ref<number | null>(null);

  const registerTodos = async () => {
    try {
      const res = await postTodos(todos.value);
      statusCode.value = res.status;
      message.value = makeSummaryMessage("作成", res.data.success_count, res.data.error_count);
      message.value += makeMessage(res.data.results, "作成");
      todos.value = [];
    } catch (error) {
      statusCode.value = null;
      message.value = parseError(error, "Todoの登録に失敗しました");
    }
  }

  return {
    todos,
    message,
    statusCode,
    registerTodos
  }
};

export const useGetTodos = (todoMsg: Ref<string>) => {
  const todos = ref<TodoInfo[]>([]);
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
        todos.value = res.data.todos;
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
      todoMsg.value = makeSummaryMessage("終了", res.data.success_count, res.data.error_count);
      todoMsg.value += makeMessage(res.data.results, "終了");
      if (onSuccess) {
        await onSuccess();
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

        todoMsg.value = makeSummaryMessage("削除", res.data.success_count, res.data.error_count);
        todoMsg.value += makeMessage(res.data.results, "削除");
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
