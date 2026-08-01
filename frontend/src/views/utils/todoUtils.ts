import { ref, type Ref } from 'vue';
import { SingleTodoAction, TodoInfo, MultiTodoAction, UpsertTodoParam } from '../types/todo';

export const validateTodo = (todoAction: SingleTodoAction, todo: UpsertTodoParam) => {
  if (["show", "finish", "delete"].includes(todoAction)) {
    // 作成しない場合はチェックをスキップ
    return true;
  }
  return !!(todo.title && todo.due);
};

export const ConfirmTodoRequest = (
  todo: Ref<TodoInfo | undefined>,
  selectedTodoIDs: Ref<number[]>,
  newTodoTitle: Ref<string>,
  newTodoDetail: Ref<string>,
  newTodoDue: Ref<string>
) => {
  const showModal = ref(false);
  const modalTitle = ref();
  const titleError = ref<boolean>(false); // todo編集時、タイトルに入力がない場合のメッセージを表示
  const dueError = ref<boolean>(false); // todo編集時、期限に入力がない場合のメッセージを表示
  const todoAction = ref<SingleTodoAction | MultiTodoAction>("show"); // todoに対して行う操作名(閲覧、編集、終了、削除)
  const confirmSingleTodoRequest = (content: TodoInfo, action: SingleTodoAction) => {
    showModal.value = true;
    titleError.value = false;
    dueError.value = false;
    todoAction.value = action;
    selectedTodoIDs.value = [content.todo_id];

    if (action === "finish") {
      modalTitle.value = "Todo終了確認";
    } else if (action === "delete") {
      modalTitle.value = "Todo削除確認";
    } else if (action === "show") {
      modalTitle.value = "Todo閲覧";
      todo.value = content;
    } else if (action === "edit") {
      modalTitle.value = "Todo編集";
      newTodoTitle.value = content.title;
      newTodoDetail.value = content.detail;
      newTodoDue.value = content.due;
      todo.value = content;
    }
  };

  const confirmMultiTodoRequest = (action: MultiTodoAction) => {
    showModal.value = true;
    titleError.value = false;
    dueError.value = false;
    todoAction.value = action;

    if (action === "finish-multi") {
      modalTitle.value = "Todo一括終了確認";
    } else {
      modalTitle.value = "Todo一括削除確認";
    }
  };
  return {
    showModal,
    titleError,
    dueError,
    todoAction,
    modalTitle,
    confirmSingleTodoRequest,
    confirmMultiTodoRequest
  }
}
