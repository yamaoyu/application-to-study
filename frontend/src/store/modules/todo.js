export const moduleTodo = {
    namespaced: true,
    state: {
            todoInfo: {}
        },
    mutations: {
        editTodoInfo(state, todoInfo){
            state.todoInfo = todoInfo
        }
    }
}