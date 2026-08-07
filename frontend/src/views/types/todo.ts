type TodoErrorMessage =
    | "UNEXPECTED_ERROR" | "TODO_NOT_FOUND" | "TODO_ALREADY_FINISHED"

export type TodoResult =
    | {
        "title": string
        "due": string
        "detail": string
        "result": "success"
        "reason": null
    }
    | {
        "title": string
        "due": string
        "detail": string
        "result": "error"
        "reason": TodoErrorMessage
    }


export type UpsertTodoResponse = {
    "success_count": number
    "error_count": number
    "results": TodoResult[]
}

export type UpsertTodoParam = {
    "title": string
    "due": string
    "detail": string
}

export type TodoInfo = {
    "todo_id": number
    "title": string
    "due": string
    "detail": string
    "status": boolean
}

export type GetTodoResponse = {
    todos: TodoInfo[]
}

export type FinishTodoParam = {
    "ids": number[]
}

export type DeleteTodoParam = FinishTodoParam

export type GetTodosParam = {
    status?: string;
    start_due?: string;
    end_due?: string;
    title?: string;
};

export type SingleTodoAction = "show" | "edit" | "finish" | "delete" | "create";
export type MultiTodoAction = "finish-multi" | "delete-multi";
