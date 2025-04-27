<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="registerTodo">
    <div class="container col-10 d-flex justify-content-center">
      <span class="input-group-text">内容</span>
      <div class="input-group">
        <textarea
          v-model="action"
          class="form-control"
          placeholder="Todoの内容"
          maxlength="256"
          >
        </textarea>
      </div>
    </div>
    <div class="container col-8 d-flex justify-content-center mt-3">
      <div class="input-group">
        <span class="input-group-text">期限</span>
        <input
          type="date"
          v-model="due"
          class="form-control col-2"
          min="2024-01-01"
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
    <button type="submit" class="btn btn-outline-secondary mt-3">登録</button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 col-8" :class="getResponseAlert(statusCode)">{{ message }}</p>
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
    const action = ref("")
    const due = ref(getToday()); // 今日の日付を取得
    const statusCode = ref()
    const router = useRouter()
    const authStore = useAuthStore()
    const { increaseDay } = changeDate(due, message);
    const { handleError } = errorWithStatusCode(message, statusCode, router);

    const submitTodo = async() =>{
      // Todoを登録する処理
      const url = process.env.VUE_APP_BACKEND_URL + 'todos'
      const response = await axios.post(
        url, 
        { action: action.value, due: due.value},
        { headers: { Authorization: authStore.getAuthHeader}}
      )
      statusCode.value = response.status
      if (response.status===201){
        message.value = [response.data.message + "\n",
                        "内容:" + response.data.action + "\n",
                        "期限:" + response.data.due].join("")
        // フィールドをクリア
        action.value = ""
        due.value = ""
      }
    }

    const registerTodo = async() =>{
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
      action,
      due,
      statusCode,
      increaseDay,
      registerTodo,
      getResponseAlert
    }
  }
}
</script>