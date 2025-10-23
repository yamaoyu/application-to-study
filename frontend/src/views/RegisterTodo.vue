<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="registerTodos">
    <table class="table table-striped table-responsive">
      <thead class="table-dark">
        <tr>
            <th style="width: 5%;">No.</th>
            <th>内容</th>
            <th>期限</th>
            <th style="width: 8%;"></th>
            <th style="width: 8%;"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(todo, index) in todos" :key="index">
            <td class="text-center align-middle">{{ index + 1 }}</td>
            <td class="text-center align-middle todo-title" @click="openModal(todo, 'show')">{{ todo.title }}</td>
            <td class="text-center align-middle">{{ todo.due }}</td>
            <td>
              <input class="btn btn-outline-primary btn-sm" type="button" value="編集" @click="openModal(todo, 'edit')">
            </td>
            <td>
              <input class="btn btn-outline-danger btn-sm" type="button" value="削除" :data-testid="`del-todo-${index}`" @click="openModal(todo, 'delete')">
            </td>
        </tr>
        <tr class="table-secondary">
          <td colspan="5" class="text-center">
            <button 
              type="button" 
              class="btn btn-outline-primary"
              @click="openModal(todo, 'create')"
              :disabled="todos.length>=10"
              data-testid="add-todo"
            >
              + Todoを追加
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <button 
      type="submit" 
      class="btn btn-outline-secondary mt-3"
      :disabled="todos.length === 0||todos.length>=10"
      data-testid="submit-todo">登録
    </button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 col-8" :class="getResponseAlert(statusCode)" data-testid="message">{{ message }}</p>
  </div>

  <BModal 
    v-model="showModal" 
    :title="modalTitle" 
    ok-title="OK" 
    cancel-title="閉じる" 
    @ok="closeModal"
    :ok-disabled="!validateParams()"
    data-testid="modal-show"
  >
    <div v-if="todoAction==='show'||todoAction==='delete'">
      <div class="todo-detail">
          <p><strong>期限:</strong> {{ todo.due }}</p>
          <p><strong>タイトル:</strong>{{ todo.title }}</p>
          <p v-if="todo.detail"><strong>詳細:</strong> {{ todo.detail }}</p>
          <p v-else class="text-muted">Todoの詳細はありません</p>
      </div>
      <div v-if="todoAction==='delete'" style="color: red;">
        このTodoをリストから削除します
      </div>
    </div>
    <div v-else-if="todoAction==='edit'||todoAction==='create'">
      <div class="input-group">
          <label class="mt-3">
            タイトル
            <span :style="{ color: todo.title ? 'black' : 'red' }">*</span>
          </label>
          <div class="container d-flex justify-content-center">
            <div class="input-group">
                <input
                v-model="todo.title"
                class="form-control"
                :placeholder=todo.title
                maxlength="32"
                @input="titleError = !todo.title"
                data-testid="title"
                />
                <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
                {{ (todo.title || '').length }}/32
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
              v-model="todo.detail"
              class="form-control"
              :placeholder=todo.detail
              maxlength="200"
              rows="3"
              data-testid="detail"
              >
            </textarea>
            <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
              {{ (todo.detail || '').length }}/200
            </small>
          </div>
        </div>
      </div>
      <div class="input-group mt-3">
        <label>
          期限
          <span :style="{ color: todo.due ? 'black' : 'red' }">*</span>
        </label>
        <div class="container d-flex justify-content-center">
          <div class="input-group">
              <input
              type="date"
              v-model="todo.due"
              class="form-control col-2"
              :min="today"
              @input="dueError = !todo.due"
              data-testid="due"
              />
          </div>
        </div>
        <div v-if="dueError" style="color: red;">期限を入力してください</div>
      </div>
    </div>
  </BModal>
</template>

<script>
import { ref, watch } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { getResponseAlert, verifyRefreshToken, errorWithStatusCode, getToday } from './lib/index';
import { jwtDecode } from 'jwt-decode';
import { BModal } from 'bootstrap-vue-next';

export default {
  components:{
    BModal
  },

  setup() {
    const message = ref("");
    const titleError = ref(""); // todo編集時、タイトルに入力がない場合のメッセージを表示
    const dueError = ref(""); // todo編集時、期限に入力がない場合のメッセージを表示
    const todo = ref({title:"",detail:"",due:""}); // todoの情報を保持し、Todoの閲覧、編集時に使用する
    const todos = ref([]);
    const showModal = ref(false);
    const modalTitle = ref("");
    const todoAction = ref("show");
    const statusCode = ref();
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = errorWithStatusCode(statusCode, message, router);
    const today = getToday();

    const submitTodo = async() =>{
      // Todoを登録する処理
      const url = import.meta.env.VITE_BACKEND_URL + 'todos/multi';
      const response = await axios.post(
        url, 
        { todos: todos.value },
        { headers: { Authorization: authStore.getAuthHeader}}
      );
      statusCode.value = response.status;
      if (response.status===201){
        message.value = response.data.message;
        todos.value = [];
      };
    };

    const registerTodos = async() =>{
      // 登録ボタンクリック時に実行される関数
      try {
        await submitTodo();
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
            await submitTodo();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          handleError(error);
        }
      }
    };

    const validateParams = () => {
      if (["show", "finish", "delete"].includes(todoAction.value)) {
          return true;
        }
      return !!(todo.value.title && todo.value.due);
    };

    const closeModal = () => {
      showModal.value = false;
      if (todoAction.value==="create") {
        todos.value.push(todo.value);
      } else if (todo.value==="edit") {
        todo.value = content;
      } else if (todoAction.value==="delete") {
        todos.value.splice(todos.value.indexOf(todo.value), 1);
      }
      todo.value = {title:"", detail:"", due:""};
    };

    const openModal = async(content, action) =>{
      todoAction.value = action;
      showModal.value = true;
      titleError.value = null;
      dueError.value = null;
      todo.value = content;
      if (todoAction.value==="create") {
        modalTitle.value = "Todo作成";
      } else if (todoAction.value==='delete') {
        modalTitle.value = "Todo削除確認";
      } else if (todoAction.value==='show') {
        modalTitle.value = "Todo閲覧";
      } else if (todoAction.value==='edit') {
        modalTitle.value = "Todo編集";
      } else {
        modalTitle.value = "エラーが発生しました";
      }
    };

    watch(() => todos.value.length, () => {
      if (todos.value.length>=10){
        message.value = "一度に登録できるのは10件までです";
      } else if (message.value==="一度に登録できるのは10件までです") {
        message.value = "";
      }
    });

    return {
      message,
      todo,
      todos,
      todoAction,
      statusCode,
      showModal,
      modalTitle,
      titleError,
      dueError,
      today,
      registerTodos,
      getResponseAlert,
      openModal,
      validateParams,
      closeModal
    }
  }
}
</script>