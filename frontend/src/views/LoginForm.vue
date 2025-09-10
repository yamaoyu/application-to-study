<template>
  <h3>ログイン</h3>
  <form @submit.prevent="userLogin" class="container d-flex flex-column align-items-center" data-testid="login-form">
    <div class="mt-3 col-6">
      <input type="text" placeholder="username" class="form-control" v-model="username" data-testid="username" required>
    </div>
    <div class="mt-3 col-6">
      <div class="input-group">
        <input :type="!showPassword ? 'password':'text'" placeholder="password" class="form-control" v-model="password" data-testid="password" required>
        <button class="btn btn-outline-secondary" type="button"
                    @click="showPassword = !showPassword">
          <i :class="['bi', showPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
        </button>
      </div>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3" data-testid="login-button">ログイン</button>
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
      const showPassword = ref(false)
      const authStore = useAuthStore()


      onMounted(() => {
      if (route.query.message) {
      message.value = route.query.message;
      // オプション: メッセージを表示後、URLからパラメータを削除
      router.replace({ query: {} })
        }
      })
  
      const userLogin = async() => {
          if (!username.value) {
            message.value = 'ユーザー名を入力してください'
            return
          }
          if (!password.value) {
            message.value = 'パスワードを入力してください'
            return
          }
        try {
          const url = process.env.VUE_APP_BACKEND_URL + "login"
          const response = await axios.post(url, {
            username: username.value,
            password: password.value
          }, {
            withCredentials: true
          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===200){
              authStore.setAuthData(
              response.data.access_token,
              response.data.token_type,
              jwtDecode(response.data.access_token).exp)
            if (authStore.getRedirectPath){
              // ログインページの前に遷移しようとしていたページがある場合
              router.push({ path : authStore.getRedirectPath })
            } else {
              router.push({ "path" : "/home" })
            }
          }
        } catch (error) {
          statusCode.value = null;
        if (error.response){
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
        userLogin,
        showPassword
      }
    }
  }
  </script>