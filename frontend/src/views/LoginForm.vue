<template>
  <form @submit.prevent="userLogin">
    <div>
      <label for="username">ユーザー名:</label>
      <input type="text" id="username" v-model="username" required>
    </div>
    <div>
      <label for="password">パスワード:</label>
      <input type="password" id="password" v-model="password" required>
    </div>
    <button type="submit">ログイン</button>
  </form>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div>
    <router-link to="/register/user">登録はこちら</router-link>
  </div>
</template>
  
  <script>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import { useRoute, useRouter } from 'vue-router';
  import { useAuthStore } from '@/store/authenticate';
  import { jwtDecode } from 'jwt-decode';
  
  export default {
    setup() {
      const username = ref('')
      const password = ref('')
      const message = ref('')
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
        userLogin
      }
    }
  }
  </script>