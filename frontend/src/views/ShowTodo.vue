<template>
    <div class="container">
    <div class="position-relative mb-3">
        <!-- 中央に配置するためのコンテナ -->
        <h2 class="text-center">Todo一覧</h2>
        <!-- 右側に絶対配置でボタンを配置 -->
        <div class="btn-group position-absolute top-50 end-0 translate-middle-y">
            <BButton class="btn btn-outline-secondary bi-sort-down btn-sm" :variant="sortType === 'id' ? 'secondary text-white' : 'outline-secondary'" @click="sortTodos('id')">
            登録順
            </BButton>
            <BButton class="btn btn-outline-secondary bi-sort-down btn-sm" :variant="sortType === 'due' ? 'secondary text-white' : 'outline-secondary'" @click="sortTodos('due')">
            期限順
            </BButton>
        </div>
    </div>
    <!-- フィルターフォーム -->
    <div class="card mb-3">
        <div class="card-header bg-light">
            <h5 class="card-title mt-2 clickable" @click="toggleFormVisibility">
                Todoの絞り込み
                <span v-if="isFormVisible">▲</span>
                <span v-else>▼</span>
            </h5>
        </div>
        <div class="card-body collapse" :class="{ 'show': isFormVisible }">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">ステータス</label>
                    <select class="form-select" v-model="statusFilter">
                        <option value="">すべて</option>
                        <option value="true">完了</option>
                        <option value="false">未完了</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">検索範囲(以降)</label>
                    <input type="date" class="form-control" v-model="startDue">
                </div>
                <div class="col-md-4">
                    <label class="form-label">検索範囲(以前)</label>
                    <input type="date" class="form-control" v-model="endDue">
                </div>
            </div>
            <div class="d-flex justify-content-end mt-3">
                <BButton variant="secondary" class="me-2" @click="resetFilter">リセット</BButton>
                <BButton variant="primary" @click="applyFilter">フィルター適用</BButton>
            </div>
        </div>
    </div>
    <template v-if="todos.length">
        <table class="table table-striped table-responsive">
            <thead class="table-dark">
                <tr>
                    <th style="width: 5%;">No.</th>
                    <th>内容</th>
                    <th>期限</th>
                    <th>ステータス</th>
                    <th style="width: 8%;"></th>
                    <th style="width: 8%;"></th>
                    <th style="width: 8%;"></th>
                </tr>
            </thead>
            <tbody v-for="(todo, index) in todos" :key="index">
                <tr>
                    <td class="text-center align-middle">{{ index + 1 }}</td>
                    <td class="text-center align-middle todo-title" @click="confirmRequest(todo, 'show')">{{ todo.title }}</td>
                    <td class="text-center align-middle">{{ todo.due }}</td>
                    <td class="text-center align-middle fw-bold" :class="todo.status===true ? 'text-success' : 'text-danger' ">{{ BOOL_TO_STATUS[todo.status] }}</td>
                    <td><input class="btn btn-outline-primary btn-sm" type="button" value="編集" @click="confirmRequest(todo, 'edit')"></td>
                    <td><input class="btn btn-outline-success btn-sm" type="button" value="終了" @click="confirmRequest(todo, 'finish')"></td>
                    <td><input class="btn btn-outline-danger btn-sm" type="button" value="削除" @click="confirmRequest(todo, 'delete')"></td>
                </tr>
            </tbody>
        </table>
    </template>
    <div v-else class="alert alert-warning">
        {{ todoMsg }}
    </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { jwtDecode } from 'jwt-decode';
import { commonError, verifyRefreshToken } from './lib';
import { BButton } from 'bootstrap-vue-next';


export default{
    components:{
        BButton
    },

    setup() {
        const statusFilter = ref("")
        const startDue = ref()
        const endDue = ref()
        const todos = ref([])
        const todoMsg = ref("")
        const todoId = ref()
        const newTodoTitle = ref("")
        const newTodoDetail = ref("")
        const newTodoDue = ref()
        const sortType = ref("id")
        const isFormVisible = ref(false)
        const router = useRouter()
        const authStore = useAuthStore()
        const { handleError: todoError } = commonError(todoMsg, router)

        const BOOL_TO_STATUS = { "true":"完了", "false":"未完了" }

        const toggleFormVisibility = () => {
            isFormVisible.value = !isFormVisible.value
        }

        const sortTodos = async(type) =>{
            sortType.value = type
            if (sortType.value==="id"){
                todos.value.sort((item1, item2) => item1.todo_id - item2.todo_id);
            } else {
                todos.value.sort((item1, item2) => {
                if (item1.due > item2.due) return 1;
                if (item1.due < item2.due) return -1;
                return 0;
                });
            }
        }

        const applyFilter = async() =>{
            await sendGetTodoRequest()
        }

        const resetFilter = async() =>{
            statusFilter.value = ""
            startDue.value = ""
            endDue.value = ""
        }

        const renewTodos = async() =>{
        // todo更新後、データを再取得し、更新する
        try {
            const todoUrl = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
            const todoRes = await axios.get(todoUrl,
                                        {headers: {Authorization: authStore.getAuthHeader}})
            todos.value = todoRes.data;
        } catch (todo_err){
            switch (todo_err.response.status){
            case 404:
            case 500:
                todos.value = []
                todoMsg.value = todo_err.response.data.detail;
                break
            default:
                todoMsg.value = "todoの取得に失敗しました"
            }
        }
        }

        const updateTodo = async() =>{
            // 更新後のTodoを送信する処理
            const url = process.env.VUE_APP_BACKEND_URL + 'todos/' + Number(todoId.value)
            const response = await axios.put(url,
                                            {title: newTodoTitle.value, detail:newTodoDetail.value, due:newTodoDue.value},
                                            {headers: {Authorization: authStore.getAuthHeader}})
            if (response.status===200){
                await renewTodos()
            }
            }

        const editTodo = async() =>{
            // 更新ボタンを押した時に実行される関数
            try{
                await updateTodo()
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
                    await updateTodo();
                } catch (refreshError) {
                    router.push({
                    path: "/login",
                    query: { message: "再度ログインしてください" }
                    });
                }            
                } else {
                    todoError(error);
                }
            }
        }

        const getTodos = async() =>{
            let todoUrl = process.env.VUE_APP_BACKEND_URL + 'todos'
            let queryParameter = ""
            if (statusFilter.value){
                queryParameter += "status=" + statusFilter.value
            } 
            if (startDue.value){
                queryParameter += "start_due=" + startDue.value
            }
            if (endDue.value){
                queryParameter += "end_due=" + endDue.value
            }
            if (queryParameter){
                todoUrl += "?" + queryParameter
            }
            return await axios.get(todoUrl, {headers: {Authorization: authStore.getAuthHeader}})
        }

        const sendGetTodoRequest = async() =>{
            try{
                const todoRes = await getTodos()
                if (todoRes.status==200){
                    todos.value = todoRes.data;
                    todoMsg.value = ""
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
                    await updateTodo();
                } catch (refreshError) {
                    router.push({
                    path: "/login",
                    query: { message: "再度ログインしてください" }
                    });
                }            
                } else {
                    todos.value = [];
                    todoMsg.value = await todoError(todoErr);
                    console.log(todoMsg.value)
                }
            }
        }

        onMounted( async()=>{
            await sendGetTodoRequest();
        })

        return {
            todos,
            todoMsg,
            toggleFormVisibility,
            applyFilter,
            resetFilter,
            statusFilter,
            startDue,
            endDue,
            sortType,
            sortTodos,
            editTodo,
            isFormVisible,
            BOOL_TO_STATUS
        }
    }
}

</script>