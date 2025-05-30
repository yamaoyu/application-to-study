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
                    <label class="form-label">期限(以降)</label>
                    <input type="date" class="form-control" v-model="startDue">
                </div>
                <div class="col-md-4">
                    <label class="form-label">期限(以前)</label>
                    <input type="date" class="form-control" v-model="endDue">
                </div>
            </div>
            <div class="mt-3">
                <label>タイトル</label>
                <input type="text" class="form-control" v-model="title">
            </div>
            <div class="d-flex justify-content-end mt-3">
                <BButton variant="secondary" class="me-2" @click="resetFilter">リセット</BButton>
                <BButton variant="primary" @click="applyFilter">フィルター適用</BButton>
            </div>
        </div>
    </div>
    <template v-if="paginatedTodos.length">
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
            <tbody v-for="(todo, index) in paginatedTodos" :key="index">
                <tr>
                    <td class="text-center align-middle">{{ index + currentPage * 10 - 10 + 1 }}</td>
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

    <nav>
        <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="goToPage(1)" :disabled="currentPage === 1">
                    最初
                </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">
                    前へ
                </button>
            </li>
            
            <li v-for="page in visiblePages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                <button class="page-link" @click="goToPage(page)">
                    {{ page }}
                </button>
            </li>
            
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">
                    次へ
                </button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="goToPage(totalPages)" :disabled="currentPage === totalPages">
                    最後
                </button>
            </li>
        </ul>
    </nav>

    <div v-if="todoMsg" class="alert alert-warning">
        {{ todoMsg }}
    </div>
    </div>

    <BModal v-model="showModal" :title="modalTitle" :ok-title="todoAction==='show' ? 'OK' : '送信'" :cancel-title="todoAction==='show' ? '閉じる' : 'いいえ'" @ok="sendTodoRequest">
        <div v-if="todoAction==='finish' || todoAction==='delete'" class="text-danger">確定後は取り消せません</div>
            <div v-else-if="todoAction==='show'">
                <div class="todo-detail">
                    <p><strong>期限:</strong> {{ todo.due }}</p>
                    <p><strong>タイトル:</strong>{{ todo.title }}</p>
                    <p v-if="todo.detail"><strong>詳細:</strong> {{ todo.detail }}</p>
                    <p v-else class="text-muted">Todoの詳細はありません</p>
                </div>
            </div>
        <div v-else-if="todoAction==='edit'">
            <div class="input-group">
                <span>題名</span>
                <div class="container d-flex justify-content-center">
                    <div class="input-group">
                        <input
                        v-model="newTodoTitle"
                        class="form-control"
                        :placeholder=todo.title
                        maxlength="32"
                        />
                        <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
                        {{ (newTodoTitle || '').length }}/32
                        </small>
                    </div>
                </div>
            </div>
            <div class="input-group mt-3">
                <span>詳細</span>
                <div class="container d-flex justify-content-center">
                    <div class="input-group">
                        <textarea
                        v-model="newTodoDetail"
                        class="form-control"
                        :placeholder=todo.detail
                        maxlength="200"
                        rows="3"
                        >
                        </textarea>
                        <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
                        {{ (newTodoDetail || '').length }}/200
                        </small>
                    </div>
                </div>
            </div>
            <div class="input-group mt-3">
                <span>期限</span>
                <div class="container d-flex justify-content-center">
                    <div class="input-group">
                        <input
                        type="date"
                        v-model="newTodoDue"
                        class="form-control col-2"
                        min="2024-01-01"
                        />
                    </div>
                </div>
            </div>
        </div>
    </BModal>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { getTodoRequest, editTodoRequest, finishTodoRequest, deleteTodoRequest } from './lib';
import { BButton,BModal } from 'bootstrap-vue-next';


export default{
    components:{
        BButton,
        BModal
    },

    setup() {
        const statusFilter = ref("")
        const startDue = ref()
        const endDue = ref()
        const title = ref()
        const todos = ref([])
        const todoMsg = ref("")
        const showModal = ref(false)
        const modalTitle = ref()
        const todoId = ref() // todo操作の対象となるtodoのIDを保持
        const todoAction = ref() // todoに対して行う操作名(閲覧、編集、終了、削除)
        const sortType = ref("id") // todoの一覧で表示されるソート順で初期値は登録順(id)
        const todo = ref() // todoの情報を保持し、Todoの閲覧、編集時に使用する
        const newTodoTitle = ref("")
        const newTodoDetail = ref("")
        const newTodoDue = ref()
        const isFormVisible = ref(false)
        const getTodos = getTodoRequest(statusFilter, startDue, endDue, title, todos, todoMsg)
        const editTodo = editTodoRequest(todoId, newTodoTitle, newTodoDetail, newTodoDue, todoMsg, getTodos)
        const finishTodo = finishTodoRequest(todoId, todoMsg, getTodos)
        const deleteTodo = deleteTodoRequest(todoId, todoMsg, getTodos)
        const BOOL_TO_STATUS = { "true":"完了", "false":"未完了" }

        // ページネーション用の変数
        const currentPage = ref(1)
        const itemsPerPage = ref(10)
        const totalItems = computed(() => todos.value.length)
        const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
        const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
        const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, totalItems.value))
        
        const paginatedTodos = computed(() => {
            return todos.value.slice(startIndex.value, endIndex.value)
        })

        const goToPage = (page) => {
            if (page >= 1 && page <= totalPages.value) {
                currentPage.value = page
            }
        }

        // 表示するページ番号の範囲を計算
        const visiblePages = computed(() => {
            const pages = []
            const maxVisiblePages = 5
            let start = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
            let end = Math.min(totalPages.value, start + maxVisiblePages - 1)
            
            // 最後のページが表示範囲に入るように調整
            if (end - start + 1 < maxVisiblePages) {
                start = Math.max(1, end - maxVisiblePages + 1)
            }
            
            for (let i = start; i <= end; i++) {
                pages.push(i)
            }
            return pages
        })

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
            await getTodos()
        }

        const resetFilter = async() =>{
            statusFilter.value = ""
            startDue.value = ""
            endDue.value = ""
            title.value = ""
        }

        const confirmRequest = async(content, action) =>{
            showModal.value = true
            todoId.value = content.todo_id
            todoAction.value = action
            if (todoAction.value==='finish'){
                modalTitle.value = "Todo終了確認"
            } else if (todoAction.value==='delete') {
                modalTitle.value = "Todo削除確認"
            } else if (todoAction.value==='show') {
                modalTitle.value = "Todo閲覧"
                todo.value = content
            } else if (todoAction.value==='edit') {
                modalTitle.value = "Todo編集"
                newTodoTitle.value = content.title
                newTodoDetail.value = content.detail
                newTodoDue.value = content.due
                todo.value = content
            }
        }

        const sendTodoRequest = async() =>{
            if (todoAction.value==='finish'){
                await finishTodo()
            } else if (todoAction.value==='delete') {
                await deleteTodo()
            } else if (todoAction.value==='edit'){
                await editTodo()
            }
            // データを初期化
            todoId.value = null
            todoAction.value = null
            todo.value = null
        }

        onMounted( async()=>{
            await getTodos();
        })

        return {
            todo,
            todoMsg,
            showModal,
            modalTitle,
            todoAction,
            toggleFormVisibility,
            applyFilter,
            resetFilter,
            confirmRequest,
            sendTodoRequest,
            statusFilter,
            startDue,
            endDue,
            title,
            sortType,
            sortTodos,
            finishTodo,
            deleteTodo,
            editTodo,
            newTodoTitle,
            newTodoDetail,
            newTodoDue,
            isFormVisible,
            BOOL_TO_STATUS,
            totalItems,
            totalPages,
            currentPage,
            visiblePages,
            paginatedTodos,
            goToPage
        }
    }
}

</script>