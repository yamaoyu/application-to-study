import { defineStore } from 'pinia'
import { SingleTodoAction } from '@/views/types/todo'

export const useTodoStore = defineStore('todoStore', {
  state: () => ({
    todoId: NaN,
    action: "",
    due: ""
  }),
  actions: {
    saveTodo(todoId: number, action: SingleTodoAction, due: string) {
      this.todoId = todoId
      this.action = action
      this.due = due
    },
  }
})