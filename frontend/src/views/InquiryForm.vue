<template>
  <form @submit.prevent="sendInquiry" class="container d-flex flex-column align-items-center">
    <div class="mt-3 col-8">
      <p class="fw-bold">カテゴリ</p>
      <div class="mt-2">
        <label class="me-2">
          <input type="radio" value="要望" v-model="category" required>要望
        </label>
        <label class="me-2">
          <input type="radio" value="エラー報告" v-model="category" required>エラー報告
        </label>
        <label class="me-2">
          <input type="radio" value="その他" v-model="category" required>その他
        </label>
      </div>
    </div>
    <div class="mt-3 col-8">
      <label class="fw-bold">詳細(最大256文字):</label>
      <textarea id="detail" maxlength="256" v-model="detail" class="form-control mt-2" required></textarea>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3">送信</button>
  </form>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" class="col-8 mt-3" :class="getResponseAlert(statusCode)">{{ message }}</p>
  </div>
</template>
  
  <script>
  import { ref } from 'vue'
  import axios from 'axios'
  import { getResponseAlert, verfiyRefreshToken, commonError } from './lib';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/store/authenticate';
  import { jwtDecode } from 'jwt-decode';
  
  export default {
    setup() {
      const category = ref('')
      const detail = ref('')
      const message = ref('')
      const statusCode = ref()
      const router = useRouter()
      const authStore = useAuthStore()
      const { handleError } = commonError(statusCode, message, router)

      const submitInquiry = async() =>{
        // 問い合わせ送信リクエスト処理、sendInquiry関数で呼び出される
        const url = process.env.VUE_APP_BACKEND_URL + 'inquiries'
        const response = await axios.post(
          url, 
          {category: category.value, detail: detail.value},
          {headers: {Authorization: authStore.getAuthHeader}}
        )
        if (response.status===201){
          statusCode.value = response.status
          message.value = ["以下の内容で受け付けました\n",
                          `カテゴリ:${response.data.category}\n`,
                          `内容:${response.data.detail}`].join('');
        }
      }

      const sendInquiry = async() => {
        // 送信ボタンクリック時に実行される
        try {
          await submitInquiry();
        } catch (error) {
          if (error.response?.status === 401) {
          try {
            // リフレッシュトークンを検証して新しいアクセストークンを取得
            const tokenResponse = await verfiyRefreshToken();
            // 新しいアクセストークンをストアに保存
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await submitInquiry();
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
        category,
        detail,
        message,
        statusCode,
        getResponseAlert,
        sendInquiry
      }
    }
  }
  </script>