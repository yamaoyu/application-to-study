import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { jwtDecode } from 'jwt-decode';
import { commonError, verifyRefreshToken } from '../lib';

export function getTodoRequest(statusFilter, startDue, endDue, title, todos, todoMsg){
    const router = useRouter();
    const { handleError: todoError } = commonError(todoMsg, router);
    const authStore = useAuthStore();

    const sendGetTodoRequest = async() =>{
        let todoUrl = process.env.VUE_APP_BACKEND_URL + 'todos'
        let queryParameter = ""
        if (statusFilter.value){
            queryParameter += "status=" + statusFilter.value
        } 
        if (startDue.value){
            if (queryParameter){
                queryParameter += "&"
            }
            queryParameter += "start_due=" + startDue.value
        }
        if (endDue.value){
            if (queryParameter){
                queryParameter += "&"
            }
            queryParameter += "end_due=" + endDue.value
        }
        if (title.value){
            if (queryParameter){
                queryParameter += "&"
            }
            queryParameter += "title=" + title.value
        }
        if (queryParameter){
            todoUrl += "?" + queryParameter
        }
        return await axios.get(todoUrl, {headers: {Authorization: authStore.getAuthHeader}})
    }

    const getTodos = async() =>{
        try{
            const todoRes = await sendGetTodoRequest()
            if (todoRes.status==200){
                todos.value = todoRes.data;
            }
            } catch (todoErr) {
            if (todoErr.response?.status === 401) {
            try {
                // リフレッシュトークンを検証して新しいアクセストークンを取得
                const tokenResponse = await verifyRefreshToken();
                // 新しいアクセストークンをストアに保存
                await authStore.setAuthData(
                    tokenResponse.data.access_token,
                    tokenResponse.data.token_type,
                    jwtDecode(tokenResponse.data.access_token).exp);
                // 再度リクエストを送信
                await sendGetTodoRequest();
            } catch (refreshError) {
                router.push({
                path: "/login",
                query: { message: "再度ログインしてください" }
                });
            }            
            } else {
                todos.value = [];
                todoMsg.value = await todoError(todoErr);
            }
        }
    }

    return getTodos
}


export function editTodoRequest(todoId, newTodoTitle, newTodoDetail, newTodoDue, todoMsg, getTodos){
    const router = useRouter();
    const { handleError: todoError } = commonError(todoMsg, router);
    const authStore = useAuthStore();

    const sendEditTodoRequest = async() =>{
        // 更新後のTodoを送信する処理
        const url = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoId.value
        const response = await axios.put(url,
                                        {title: newTodoTitle.value, detail:newTodoDetail.value, due:newTodoDue.value},
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.status===200){
            todoMsg.value = response.data.message;
            await getTodos();
        }
    }

    const editTodo = async() =>{
        // 更新ボタンを押した時に実行される関数
        try{
            await sendEditTodoRequest()
        } catch (error) {
            if (error.response?.status === 401) {
            try {
                // リフレッシュトークンを検証して新しいアクセストークンを取得
                const tokenResponse = await verifyRefreshToken();
                // 新しいアクセストークンをストアに保存
                await authStore.setAuthData(
                    tokenResponse.data.access_token,
                    tokenResponse.data.token_type,
                    jwtDecode(tokenResponse.data.access_token).exp);
                // 再度リクエストを送信
                await sendEditTodoRequest();
            } catch (refreshError) {
                router.push({
                path: "/login",
                query: { message: "再度ログインしてください" }
                });
            }            
            } else {
                todoMsg.value = await todoError(error);
            }
        }
    }

    return editTodo
}


export function finishTodoRequest(todoId, todoMsg, getTodos) {
    const router = useRouter();
    const { handleError: todoError } = commonError(todoMsg, router);
    const authStore = useAuthStore();

    const sendFinishTodoRequest = async() =>{
        const finish_url = process.env.VUE_APP_BACKEND_URL + 'todos/finish/' + todoId.value
        const response = await axios.put(
            finish_url, 
            {},
            { 
            headers: {
            Authorization: authStore.getAuthHeader}
            }
        )
        return response
    }

    const finishTodo = async() =>{
        try {
            const response = await sendFinishTodoRequest(todoId.value)
            if (response.status===200){
                todoMsg.value = response.data.message;
                await getTodos();
            }
        } catch (error) {
            if (error.response?.status === 401) {
                try {
                    // リフレッシュトークンを検証して新しいアクセストークンを取得
                    const tokenResponse = await verifyRefreshToken();
                    // 新しいアクセストークンをストアに保存
                    await authStore.setAuthData(
                    tokenResponse.data.access_token,
                    tokenResponse.data.token_type,
                    jwtDecode(tokenResponse.data.access_token).exp)
                    // 再度リクエストを送信
                    await sendFinishTodoRequest(todoId.value);
                    await getTodos();
                } catch (refreshError) {
                    router.push({
                    path: "/login",
                    query: { message: "再度ログインしてください" }
                    });
                }            
            } else {
                todoMsg.value = await todoError(error)
            }
        }
    }

    return finishTodo
}

export function deleteTodoRequest(todoId, todoMsg, getTodos) {
    const router = useRouter();
    const { handleError: todoError } = commonError(todoMsg, router);
    const authStore = useAuthStore();

    const sendDeleteTodoRequest = async() =>{
        const deleteUrl = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoId.value
        const response = await axios.delete(
            deleteUrl, 
            { 
            headers: {
            Authorization: authStore.getAuthHeader}
            }
        )
        return response
    }

    const deleteTodo = async() =>{
        try {
            const response = await sendDeleteTodoRequest(todoId.value);
            if (response.status===204){
                todoMsg.value = "選択したtodoを削除しました";
                await getTodos();
            }
        } catch (error) {
            if (error.response?.status === 401) {
            try {
                // リフレッシュトークンを検証して新しいアクセストークンを取得
                const tokenResponse = await verifyRefreshToken();
                // 新しいアクセストークンをストアに保存
                await authStore.setAuthData(
                tokenResponse.data.access_token,
                tokenResponse.data.token_type,
                jwtDecode(tokenResponse.data.access_token).exp)
                // 再度リクエストを送信
                await sendDeleteTodoRequest(todoId);
                await getTodos();
            } catch (refreshError) {
                router.push({
                path: "/login",
                query: { message: "再度ログインしてください" }
                });
            }            
            } else {
                todoMsg.value = await todoError(error)
            }
        }
    }
    return deleteTodo
}