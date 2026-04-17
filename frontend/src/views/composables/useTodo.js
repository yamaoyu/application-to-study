import { ref } from "vue";
import { postTodos, getTodos, editTodo, finishTodos, deleteTodos } from "../api/todo";
import { parseError } from "../utils/error";

export const useRegisterTodos = () =>{
  const todos = ref([]);
  const message = ref("");
  const statusCode = ref();

  const regitserTodos = async() =>{
    try {
      const res = await postTodos(todos.value);
      if (res.status===201) {
        statusCode.value = res.status;
        message.value = res.data.message;
        todos.value = [];
      }
    } catch(error) {
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

export const useGetTodos = (todoMsg) => {
  const todos = ref([]);
  const statusFilter = ref(null);
  const startDue = ref();
  const endDue = ref();
  const title = ref();

  const makeQuery = () => {
    let queryParameter = "";
    if (statusFilter.value){
      queryParameter += "status=" + statusFilter.value;
    } 
    if (startDue.value){
      if (queryParameter){
        queryParameter += "&"
      }
      queryParameter += "start_due=" + startDue.value;
    }
    if (endDue.value){
      if (queryParameter){
        queryParameter += "&"
      }
      queryParameter += "end_due=" + endDue.value;
    }
    if (title.value){
      if (queryParameter){
        queryParameter += "&"
      }
      queryParameter += "title=" + title.value;
    }

    return queryParameter;
  }

  const fetchTodos = async() => {
    try {
      const query = makeQuery();
      const res = await getTodos(query);
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

export const useTodoOperations = (todoMsg) => {
  const selectedTodoIDs = ref([]); // 一括操作するtodoのIDを保持
  const newTodoTitle = ref("");
  const newTodoDetail = ref("");
  const newTodoDue = ref();

  const updateTodo = async(id, onSuccess) => {
    try {
      const params = {
        title:newTodoTitle.value,
        detail:newTodoDetail.value,
        due:newTodoDue.value
      };
      const res = await editTodo(id, params);
      if (res.status === 200) {
        todoMsg.value = res.data.message;
        if (onSuccess) {
          await onSuccess();
        }
      }
    } catch (error) {
      todoMsg.value = parseError(error, "Todoの更新に失敗しました");
    }
  };

  const completeTodos = async(onSuccess) => {
    try {
      const params = { "ids": selectedTodoIDs.value }
      const res = await finishTodos(params);
      if (res.status === 200) {
        todoMsg.value = `${res.data.message}\n${res.data.titles}`;
        if (onSuccess) {
          await onSuccess();
        }
      }
    } catch (error) {
      todoMsg.value = parseError(error, "Todoの終了に失敗しました");
    }
  };

  const removeTodos = async(onSuccess) => {
    try {
      const params = { "ids": selectedTodoIDs.value };
      const res = await deleteTodos(params);
      if (res.status === 204) {
        todoMsg.value = "選択したTodoを削除しました";
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

export const useSortTodos = (todos) => {
  const sortType = ref("id"); // todoの一覧で表示されるソート順で初期値は登録順(id)

  const sortTodos = async(type) =>{
    sortType.value = type;
    if (sortType.value==="id"){
      todos.value.sort((item1, item2) => item1.todo_id - item2.todo_id);
    } else {
      todos.value.sort((item1, item2) => {
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
