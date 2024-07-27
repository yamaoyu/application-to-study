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
  </template>
  
  <script>
  import { ref, onMounted } from 'vue'
  // import { ref } from 'vue'
  import axios from 'axios'
  import { useRoute, useRouter } from 'vue-router';
  
  export default {
    setup() {
      const username = ref('')
      const password = ref('')
      const message = ref('')
      const router =  useRouter()
      const route = useRoute()

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
          message.value = response.data.message;
          router.push({
            "path":"/",
            "query":{message:response.data.message}})
        } catch (error) {
          // エラー処理（ユーザーへの通知など）
          message.value = "ユーザーログイン失敗";
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