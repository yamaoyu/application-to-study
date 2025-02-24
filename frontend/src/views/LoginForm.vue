<template>
  <h3>ログイン</h3>
  <form @submit.prevent="userLogin" class="container d-flex flex-column align-items-center">
    <div class="mt-3 col-6">
      <input type="text" placeholder="username" class="form-control" v-model="username" required>
    </div>
    <div class="mt-3 col-6">
      <input type="password" placeholder="password" class="form-control" v-model="password" required>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3">ログイン</button>
  </form>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" :class="getResponseAlert(statusCode)" class="mt-3 col-8">{{ message }}</p>
  </div>
  <div class="mt-3">
    <router-link to="/register/user">登録はこちら</router-link>
  </div>
</template>
  
  <script>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import { useRoute, useRouter } from 'vue-router';
  import { useAuthStore } from '@/store/authenticate';
  import { jwtDecode } from 'jwt-decode';
  import { getResponseAlert } from './lib';

  export default {
    setup() {
      const username = ref('')
      const password = ref('')
      const message = ref('')
      const statusCode = ref()
      const router =  useRouter()
      const route = useRoute()
      const authStore = useAuthStore()


      onMounted(() => {
      if (route.query.message) {
      message.value = route.query.message;
      // オプション: メッセージを表示後、URLからパラメータを削除
      router.replace({ query: {} })
        }
      })
  
      const userLogin = async() => {
        try {
          // デバイス情報を取得 HTTPSにするまでの一時的な対応としてplatform(非推奨)を使用
          const device = navigator?.platform || "unknown";
          const url = process.env.VUE_APP_BACKEND_URL + "login"
          const response = await axios.post(url, {
            username: username.value,
            password: password.value,
            device: device
          }, {
            withCredentials: true
          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===200){
              authStore.setAuthData(
              response.data.access_token,
              response.data.token_type,
              jwtDecode(response.data.access_token).exp)

            router.push({
              "path":"/home"})
          }
        } catch (error) {
        if (error.response){
          statusCode.value = error.response.status;
          switch (error.response.status){
            case 422:
              message.value = error.response.data.detail;
              break;
            case 500:
              message.value =  "ログインに失敗しました"
              break;
            default:
              message.value = error.response.data.detail;}
          } else if (error.request){
            console.log(error.request)
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }  
      return {
        username,
        password,
        message,
        statusCode,
        getResponseAlert,
        userLogin
      }
    }
  }
  </script>