export const validateTodo = (todoAction, todo) => {
  if (["show", "finish", "delete"].includes(todoAction)) {
    // 作成しない場合はチェックをスキップ
    return true;
  }
  return !!(todo.title && todo.due);
};
