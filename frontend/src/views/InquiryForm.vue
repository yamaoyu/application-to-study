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
  import { getResponseAlert } from './lib';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/store/authenticate';
  
  export default {
    setup() {
      const category = ref('')
      const detail = ref('')
      const message = ref('')
      const statusCode = ref()
      const router = useRouter()
      const authStore = useAuthStore()
  
      const sendInquiry = async() => {
        try {
          const url = process.env.VUE_APP_BACKEND_URL + 'inquiries'
          const response = await axios.post(
            url, 
            {
              category: category.value,
              detail: detail.value,
            },
            {
              headers: {
                Authorization: authStore.getAuthHeader}
            }
          )
          if (response.status===201){
            statusCode.value = response.status
            message.value = ["以下の内容で受け付けました\n",
                            `カテゴリ:${response.data.category}\n`,
                            `内容:${response.data.detail}`].join('');
          }
        } catch (error) {
          statusCode.value = null;
          if (error.response){
            switch (error.response.status){
              case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
                break;
              case 422:
                message.value = error.response.data.detail;
                break;
              case 500:
                message.value =  "問い合わせの送信に失敗しました"
                break;
              default:
                message.value = error.response.data.detail;}
          } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
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