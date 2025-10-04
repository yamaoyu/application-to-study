<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="registerTodo">
    <label class="mt-3">
      題名
      <span :style="{ color: title ? 'black' : 'red' }">*</span>
    </label>
    <div class="container d-flex col-10 justify-content-center">
      <div class="input-group">
        <input
          v-model="title"
          class="form-control col-10"
          placeholder="Todoのタイトル"
          maxlength="32"
          data-testid="todo-title"
          required
          />
        <span class="input-group-text">{{ title.length }}/32</span>
      </div>
    </div>
    <label class="mt-3">詳細</label>
    <div class="container d-flex col-10 justify-content-center mt-3">
      <div class="input-group">
        <textarea
          v-model="detail"
          class="form-control col-10"
          placeholder="Todoの詳細"
          maxlength="200"
          rows="4"
          data-testid="todo-detail"
          >
        </textarea>
        <span class="input-group-text">{{ detail.length }}/200</span>
      </div>
    </div>
    <label class="mt-3">
      期限
      <span :style="{ color: due ? 'black' : 'red' }">*</span>
    </label>
    <div class="container col-8 d-flex justify-content-center mt-3">
      <div class="input-group">
        <input
          type="date"
          v-model="due"
          class="form-control col-2"
          min="2024-01-01"
          data-testid="todo-due"
          required
        />
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseDay(-1)"
          >
          前日
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseDay(1)"
          >
          翌日
        </button>
      </div>
    </div>
    <button 
      type="submit" 
      class="btn btn-outline-secondary mt-3" 
      data-testid="submit-todo">登録
    </button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 col-8" :class="getResponseAlert(statusCode)" data-testid="message">{{ message }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { changeDate, getResponseAlert, getToday, verifyRefreshToken, errorWithStatusCode } from './lib/index';
import { jwtDecode } from 'jwt-decode';

export default {
  setup() {
    const message = ref("")
    const title = ref("")
    const detail = ref("")
    const due = ref(getToday()); // 今日の日付を取得
    const statusCode = ref()
    const router = useRouter()
    const authStore = useAuthStore()
    const { increaseDay } = changeDate(due, message);
    const { handleError } = errorWithStatusCode(statusCode, message, router);

    const submitTodo = async() =>{
      // Todoを登録する処理
      const url = import.meta.env.VITE_BACKEND_URL + 'todos'
      const response = await axios.post(
        url, 
        { title: title.value, detail: detail.value, due: due.value},
        { headers: { Authorization: authStore.getAuthHeader}}
      )
      statusCode.value = response.status
      if (response.status===201){
        message.value = [response.data.message + "\n",
                        "タイトル:" + response.data.title + "\n",
                        "詳細:" + response.data.detail + "\n",
                        "期限:" + response.data.due].join("")
        // フィールドをクリア
        title.value = ""
        detail.value = ""
        due.value = ""
      }
    }

    const registerTodo = async() =>{
      // データの検証
      if (!title.value) {
        message.value = 'タイトルを入力してください'
        return
      }
      if (!due.value) {
        message.value = '期限を入力してください'
        return
      }
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
          handleError(error)
        }
      }
    }

    return {
      message,
      title,
      detail,
      due,
      statusCode,
      increaseDay,
      registerTodo,
      getResponseAlert
    }
  }
}
</script>