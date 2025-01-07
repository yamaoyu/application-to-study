import { defineStore } from 'pinia'

export const useTodoStore = defineStore('todoStore',{
    state: () => ({
            todoId: null,
            action: null,
            due: null
        }),
    actions: {
      saveTodo(todoId, action, due) {
        this.todoId = todoId
        this.action = action
        this.due = due
      },
    }
})