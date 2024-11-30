<template>
  <form @submit.prevent="UserLogin">
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
  import { useStore } from 'vuex';
  import { jwtDecode } from 'jwt-decode';
  
  export default {
    setup() {
      const username = ref('')
      const password = ref('')
      const message = ref('')
      const router =  useRouter()
      const route = useRoute()
      const store = useStore()


      onMounted(() => {
      if (route.query.message) {
      message.value = route.query.message;
      // オプション: メッセージを表示後、URLからパラメータを削除
      router.replace({ query: {} })
        }
      })
  
      const UserLogin = async() => {
        try {
          const response = await axios.post('http://localhost:8000/login', {
            username: username.value,
            password: password.value,
          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===200){
              store.commit('SET_AUTH_DATA', {
              accessToken: response.data.access_token,
              tokenType: response.data.token_type,
              expire: jwtDecode(response.data.access_token).exp})
            
            // Axiosのデフォルトヘッダーにトークンを設定
            axios.defaults.headers.common['Authorization'] = `${response.data.token_type} ${response.data.access_token}`

            router.push({
              "path":"/home"})
          }
        } catch (error) {
        if (error.response){
          switch (error.response.status){
            case 422:
              message.value = error.response.data.error;
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
        UserLogin
      }
    }
  }
  </script>