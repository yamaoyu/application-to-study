<template>
  <div class="container">
    <h2 class="mt-2 mb-4">{{ date }}の活動実績</h2>
    <div class="row" v-if="activityRes?.status === 200">
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
      <p v-if="activityMsg" class="col-8" :class="getActivityAlert(activityStatus)" data-testid="activity-msg">
          {{ activityMsg }}
      </p>
    </div>
  </div>
  <div class="container">
    <h2>今月の給料</h2>
    <div class="row justify-content-center mb-4" v-if="incomeRes?.status === 200">
      <div class="col-8 mb-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getSalaryColors(incomeRes.data.total_income-incomeRes.data.month_info.salary)" class="h3 fw-bold text-center" data-testid="total-income">
              {{ incomeRes.data.total_income }}
            </span>
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
            <span :class="getSalaryColors(incomeRes.data.pay_adjustment)" class="h3 fw-bold text-center">{{ incomeRes.data.pay_adjustment }}</span>
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
    <div v-else class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="incomeMsg" class="col-8 alert alert-warning p-3" data-testid="income-msg">
          {{ incomeMsg }}
      </p>
    </div>
  </div>
  <div class="container">
    <div class="position-relative mb-3">
      <!-- 中央に配置するためのコンテナ -->
      <h2 class="text-center">未完了のTodo</h2>
      <!-- 右側に絶対配置でボタンを配置 -->
      <div class="btn-group position-absolute top-50 end-0 translate-middle-y" v-if="todos.length">
        <BButton class="btn btn-outline-secondary bi-sort-down btn-sm" :variant="sortType === 'id' ? 'secondary text-white' : 'outline-secondary'" @click="sortTodos('id')" data-testid="sort-todos-id">
          登録順
        </BButton>
        <BButton class="btn btn-outline-secondary bi-sort-down btn-sm" :variant="sortType === 'due' ? 'secondary text-white' : 'outline-secondary'" @click="sortTodos('due')" data-testid="sort-todos-due">
          期限順
        </BButton>
      </div>
    </div>
    <table class="table table-striped table-responsive" v-if="todos.length">
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
        <tr data-testid="todo-row">
          <td class="text-center align-middle">{{ index + 1 }}</td>
          <td class="text-center align-middle todo-title" @click="confirmRequest(todo, 'show')">{{ todo.title }}</td>
          <td class="text-center align-middle">{{ todo.due }}</td>
          <td><input class="btn btn-outline-primary btn-sm" :data-testid="`edit-${index}`" type="button" value="編集" @click="confirmRequest(todo, 'edit')"></td>
          <td><input class="btn btn-outline-success btn-sm" :data-testid="`finish-${index}`" type="button" value="終了" @click="confirmRequest(todo, 'finish')"></td>
          <td><input class="btn btn-outline-danger btn-sm" :data-testid="`delete-${index}`" type="button" value="削除" @click="confirmRequest(todo, 'delete')"></td>
        </tr>
      </tbody>
    </table>
    <nav v-if="Object.keys(paginatedTodos).length > 0">
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
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="todoMsg" class="col-8 alert alert-success p-3" data-testid="todo-msg">
        {{ todoMsg }}
      </p>
    </div>

  <BModal 
    v-model="showModal" 
    :title="modalTitle" 
    :ok-title="todoAction==='show' ? 'OK' : '送信'" 
    :cancel-title="todoAction==='show' ? '閉じる' : 'いいえ'" 
    @ok="sendTodoRequest"
    :ok-disabled="!validateParams()"
    data-testid="modal-show"
  >
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
        <label class="mt-3">
          タイトル
          <span :style="{ color: newTodoTitle ? 'black' : 'red' }">*</span>
        </label>
        <div class="container d-flex justify-content-center">
          <div class="input-group">
            <input
              v-model="newTodoTitle"
              class="form-control"
              :placeholder=todo.title
              maxlength="32"
              @input="titleError = !newTodoTitle"
              data-testid="new-title"
              />
            <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
              {{ (newTodoTitle || '').length }}/32
            </small>
          </div>
          <div v-if="titleError" style="color: red;">タイトルを入力してください</div>
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
              data-testid="new-detail"
              >
            </textarea>
            <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
              {{ (newTodoDetail || '').length }}/200
            </small>
          </div>
        </div>
      </div>
      <div class="input-group mt-3">
        <label>
          期限
          <span :style="{ color: newTodoDue ? 'black' : 'red' }">*</span>
        </label>
        <div class="container d-flex justify-content-center">
          <div class="input-group">
            <input
              type="date"
              v-model="newTodoDue"
              class="form-control col-2"
              min="2024-01-01"
              @input="dueError = !newTodoDue"
              data-testid="new-due"
            />
          </div>
        </div>
        <div v-if="dueError" style="color: red;">期限を入力してください</div>
      </div>
    </div>
  </BModal>

</template>


<script>
import { onMounted, ref } from 'vue';
import { BButton, BModal } from 'bootstrap-vue-next';
import { usePage } from './composables/usePage';
import { useFetchActivtyByDay } from './composables/useActivitesFetch';
import { useGetTodos, useTodoOperations, useSortTodos } from './composables/useTodo';
import { useFetchMonthlySalary } from './composables/useSalary';
import { STATUS_DICT, getAdjustmentColors, getStatusColors, getActivityAlert, getSalaryColors } from './utils/ui';
import { getThisMonth } from './utils/date';

export default {
  components:{
    BModal,
    BButton
  },

  setup() {
    const activityStatus = ref("");
    const todoMsg = ref("");
    const showModal = ref(false);
    const modalTitle = ref("");
    const todoAction = ref(); // todoに対して行う操作名(閲覧、編集、終了、削除)
    const todo = ref(); // todoの情報を保持し、Todoの閲覧、編集時に使用する
    const titleError = ref(""); // todo編集時、タイトルに入力がない場合のメッセージを表示
    const dueError = ref(""); // todo編集時、期限に入力がない場合のメッセージを表示
    const { fetchMsg: incomeMsg, fetchRes: incomeRes, fetchMonthlySalary } = useFetchMonthlySalary();
    const { todos, statusFilter, fetchTodos } = useGetTodos(todoMsg);
    const { selectedTodoIDs, newTodoTitle, newTodoDetail, newTodoDue, updateTodo, completeTodos, removeTodos } = useTodoOperations(todoMsg);
    const { totalItems, totalPages, currentPage, visiblePages, paginatedTodos, goToPage } = usePage(todos, 5);
    const { sortType, sortTodos } = useSortTodos(todos);
    const { date, checkMsg: activityMsg, activityRes, fetchActivityByDay } = useFetchActivtyByDay();


    const validateParams = () => {
      if (["show", "finish", "delete"].includes(todoAction.value)) {
          return true;
        }
      return !!(newTodoTitle.value && newTodoDue.value);
    };

    const confirmRequest = async(content, action) =>{
      titleError.value = null;
      dueError.value = null;
      selectedTodoIDs.value = [content.todo_id];
      todoAction.value = action;
      todo.value = content;
      if (todoAction.value==='finish'){
        modalTitle.value = "Todo終了確認"
      } else if (todoAction.value==='delete') {
        modalTitle.value = "Todo削除確認"
      } else if (todoAction.value==='show') {
        modalTitle.value = "Todo閲覧"
      } else if (todoAction.value==='edit') {
        modalTitle.value = "Todo編集"
        newTodoTitle.value = content.title
        newTodoDetail.value = content.detail
        newTodoDue.value = content.due
      }
      showModal.value = true;
    };

    const sendTodoRequest = async() =>{
      if (todoAction.value==='finish'){
        await completeTodos();
      } else if (todoAction.value==='delete') {
        await removeTodos();
        if (currentPage.value > totalPages.value) {
            currentPage.value = totalPages.value;
        };
      } else if (todoAction.value==='edit'){
        await updateTodo(todo.value.todo_id);
      }
      // データを初期化
      todoAction.value = null;
      todo.value = null;
      selectedTodoIDs.value = [];
      await fetchTodos();
    };

    onMounted( async() =>{
      // その日の活動実績を取得
      await fetchActivityByDay();

      // その月の月収を取得
      const [year, month] = getThisMonth().split("-");
      await fetchMonthlySalary(year, month);

      // そのユーザーの未完了のtodoを取得、このページでは未完了のTodoのみを表示
      statusFilter.value = "false";
      await fetchTodos();
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
      todoAction,
      date,
      todo,
      titleError,
      dueError,
      validateParams,
      confirmRequest,
      sendTodoRequest,
      sortTodos,
      sortType,
      newTodoTitle,
      newTodoDetail,
      newTodoDue,
      STATUS_DICT,
      getAdjustmentColors,
      getStatusColors,
      getActivityAlert,
      getSalaryColors,
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