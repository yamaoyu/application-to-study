import { ref } from "vue";
import { UpsertTodoParam, SingleTodoAction } from "../types/todo";

export const useTodoModal = () => {
  const showModal = ref<boolean>(false);
  const modalTitle = ref<string>("");
  const todoAction = ref<SingleTodoAction>("show");
  const todo = ref<UpsertTodoParam>({ title: "", detail: "", due: "" });

  const openModal = (content: UpsertTodoParam, action: SingleTodoAction) => {
    todoAction.value = action;
    showModal.value = true;
    todo.value = content;

    switch (action) {
      case 'create': modalTitle.value = "Todo作成"; break
      case 'delete': modalTitle.value = "Todo削除確認"; break
      case 'show': modalTitle.value = "Todo閲覧"; break
      case 'edit': modalTitle.value = "Todo編集"; break
    }
  };

  const closeModal = (todos: UpsertTodoParam[]) => {
    showModal.value = false;
    if (todoAction.value === "create") {
      todos.push(todo.value);
    } else if (todoAction.value === "delete") {
      todos.splice(todos.indexOf(todo.value), 1);
    };
    todo.value = { title: "", detail: "", due: "" };
  };

  return {
    showModal,
    modalTitle,
    todoAction,
    todo,
    openModal,
    closeModal
  }
};
