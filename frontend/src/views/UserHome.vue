<template>
  <div class="container">
    <h2 class="mt-2 mb-4">{{ year }}年{{ month }}月{{ date }}日の活動実績</h2>
    <div class="row" v-if="activityRes">
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">目標時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activityRes.data.target_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">活動時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activityRes.data.actual_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ステータス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getStatusColors[activityRes.data.status]" class="h3 fw-bold text-center">{{ STATUS_DICT[activityRes.data.status] }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="activityMsg" class="col-8" :class="getActivityAlert(activityStatus)">
          {{ activityMsg }}
      </p>
    </div>
  </div>
  <div class="container">
    <h2>今月の給料</h2>
    <div class="row justify-content-center mb-4" v-if="incomeRes">
      <div class="col-8 mb-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(incomeRes)" class="h3 fw-bold text-center">{{ incomeRes.data.total_income }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">月収</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ incomeRes.data.month_info.salary }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス-ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(incomeRes)" class="h3 fw-bold text-center">{{ incomeRes.data.pay_adjustment }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center text-success">{{ incomeRes.data.month_info.total_bonus }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center text-danger">{{ incomeRes.data.month_info.total_penalty }}</span>
            万円
          </div>
        </div>
      </div>
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="incomeMsg" class="col-8 alert alert-warning p-3">
          {{ incomeMsg }}
      </p>
    </div>
  </div>
  <div class="container">
    <div class="position-relative mb-3">
      <!-- 中央に配置するためのコンテナ -->
      <h2 class="text-center">未完了のTodo</h2>
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
    <template v-if="todos.length">
      <table class="table table-striped table-responsive">
        <thead class="table-dark">
          <tr>
            <th style="width: 5%;">No.</th>
            <th>内容</th>
            <th>期限</th>
            <th style="width: 8%;"></th>
            <th style="width: 8%;"></th>
            <th style="width: 8%;"></th>
          </tr>
        </thead>
        <tbody v-for="(todo, index) in paginatedTodos" :key="index">
          <tr>
            <td class="text-center align-middle">{{ index + 1 }}</td>
            <td class="text-center align-middle todo-title" @click="confirmRequest(todo, 'show')">{{ todo.title }}</td>
            <td class="text-center align-middle">{{ todo.due }}</td>
            <td><input class="btn btn-outline-primary btn-sm" type="button" value="編集" @click="confirmRequest(todo, 'edit')"></td>
            <td><input class="btn btn-outline-success btn-sm" type="button" value="終了" @click="confirmRequest(todo, 'finish')"></td>
            <td><input class="btn btn-outline-danger btn-sm" type="button" value="削除" @click="confirmRequest(todo, 'delete')"></td>
          </tr>
        </tbody>
      </table>
    </template>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="todoMsg" class="col-8 alert alert-warning p-3">
        {{ todoMsg }}
      </p>
    </div>
  </div>
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
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { STATUS_DICT, getAdjustmentColors, getStatusColors, getActivityAlert, getTodoRequest, editTodoRequest, finishTodoRequest, deleteTodoRequest } from './lib';
import { BButton, BModal } from 'bootstrap-vue-next';

export default {
  components:{
    BModal,
    BButton
  },

  setup() {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth() + 1;
    const date = today.getDate();
    const activityMsg = ref("")
    const activityRes = ref()
    const activityStatus = ref("")
    const incomeMsg = ref("")
    const incomeRes = ref()
    const todos = ref([]) // 取得した全てのtodo
    const todoMsg = ref("")
    const showModal = ref(false)
    const modalTitle = ref("")
    const todoId = ref() // todo操作の対象となるtodoのIDを保持
    const todoAction = ref() // todoに対して行う操作名(閲覧、編集、終了、削除)
    const sortType = ref("id") // todoの一覧で表示されるソート順で初期値は登録順(id)
    const todo = ref() // todoの情報を保持し、Todoの閲覧、編集時に使用する
    const newTodoTitle = ref("")
    const newTodoDetail = ref("")
    const newTodoDue = ref()
    const router = useRouter()
    const authStore = useAuthStore()
    const statusFilter = ref("false")
    const startDue = ref()
    const endDue = ref()
    const title = ref()
    const getTodos = getTodoRequest(statusFilter, startDue, endDue, title, todos, todoMsg)
    const editTodo = editTodoRequest(todoId, newTodoTitle, newTodoDetail, newTodoDue, todoMsg, getTodos)
    const finishTodo = finishTodoRequest(todoId, todoMsg, getTodos)
    const deleteTodo = deleteTodoRequest(todoId, todoMsg, getTodos)

    const currentPage = ref(1)
    const itemsPerPage = ref(5)
    const totalItems = computed(() => todos.value.length)
    const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
    const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
    const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, totalItems.value))

    const paginatedTodos = computed(() =>{
      return todos.value.slice(startIndex.value, endIndex.value)
      }
    )

    const goToPage = (page) =>{
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    const visiblePages = computed(() =>{
      const pages = []
      const maxVisiblePages = 5
      let start = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
      let end = Math.min(totalPages.value, start + maxVisiblePages - 1)

      // 最後のページが表示範囲に入るように調整
      if (end - start + 1 < maxVisiblePages) {
          start = Math.max(1, end - maxVisiblePages + 1)
      }

      for (let i = start; i <= end; i ++){
        pages.push(i)
      }

      return pages
    })

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

    onMounted( async() =>{
      // その日の活動実績を取得
      try {
        const act_url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + date;
        activityRes.value = await axios.get(act_url,
                                            {headers: {Authorization: authStore.getAuthHeader}})
        if (activityRes.value.status===200){
          activityStatus.value = activityRes.value.data.status
          const bonusInYen = parseInt(activityRes.value.data.bonus * 10000, 10)
          const penaltyInYen = parseInt(activityRes.value.data.penalty * 10000, 10)
          if (activityRes.value.data.status === "success"){
            activityMsg.value = `目標達成!|\nボーナス:${activityRes.value.data.bonus}万円(${bonusInYen}円)`
          } else if(activityRes.value.data.status === "failure"){
            activityMsg.value = `目標失敗...\nペナルティ:${activityRes.value.data.penalty}万円(${penaltyInYen}円)`
          } else {
            if (activityRes.value.data.target_time <= activityRes.value.data.actual_time) {
            activityMsg.value = `目標達成!活動を終了してください\n確定後のボーナス:${activityRes.value.data.bonus}万円(${bonusInYen}円)`
            } else {
            activityMsg.value = `このままだと、${activityRes.value.data.penalty}万円(${penaltyInYen}円)のペナルティが発生`}
          }
        }
      } catch (act_err) {
        activityStatus.value = ""
        if (act_err.response){
          switch (act_err.response.status){
            case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
              break;
            case 404:
            case 500:
              activityMsg.value = act_err.response.data.detail;
              break;
            default:
              activityMsg.value = "情報の取得に失敗しました";}
        } else if (act_err.request){
          activityMsg.value =  "リクエストがサーバーに到達できませんでした"
        } else {
          activityMsg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
        }
      }

      // その月の月収を取得
      try{
        const income_url = process.env.VUE_APP_BACKEND_URL + 'incomes/' + year + '/' + month;
        incomeRes.value = await axios.get(income_url,
                                        {headers: {Authorization: authStore.getAuthHeader}}
        )
      } catch (income_err) {
        if (income_err.response){
          switch (income_err.response.status){
            case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
              break;
            case 404:
            case 500:
              incomeMsg.value = income_err.response.data.detail;
              break;
            default:
              incomeMsg.value = "情報の取得に失敗しました";}
        } else if (income_err.request){
          incomeMsg.value =  "リクエストがサーバーに到達できませんでした"
        } else {
          incomeMsg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
        }
      }

        // そのユーザーの未完了のtodoを取得
        await getTodos()
      }
    )

    return {
      activityMsg,
      activityRes,
      activityStatus,
      incomeMsg,
      incomeRes,
      todos,
      todoMsg,
      showModal,
      modalTitle,
      todoId,
      todoAction,
      year,
      month,
      date,
      todo,
      confirmRequest,
      sendTodoRequest,
      sortTodos,
      sortType,
      renewTodos,
      deleteTodo,
      finishTodo,
      editTodo,
      newTodoTitle,
      newTodoDetail,
      newTodoDue,
      STATUS_DICT,
      getAdjustmentColors,
      getStatusColors,
      getActivityAlert,
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

<style>
li{
  list-style: none;
}
.todo-item {
  margin: 0; /* 要素間の余白を削除 */
  padding: 0;
  line-height: 1.5; /* 行の高さを調整 */
}
.todo-title {
  text-decoration: underline;
  cursor: pointer;
  color: #0d6efd; /* Bootstrap primary color */
}
.todo-title:hover {
  color: #0a58ca; /* Darker shade on hover */
}
</style>