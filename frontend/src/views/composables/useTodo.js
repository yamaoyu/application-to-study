import { ref } from "vue";
import { postTodos } from "../api/todo";
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
