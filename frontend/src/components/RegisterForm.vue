<template>
    <form @submit.prevent="handleSubmit">
      <div>
        <label for="username">ユーザー名:</label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div>
        <label for="password">パスワード:</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <div>
        <label for="email">email:</label>
        <input type="email" id="email" v-model="email">
      </div>
      <button type="submit">登録</button>
    </form>
    <p v-if="message">{{ message }}</p>
</template>
  
  <script>
  import { ref } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router';
  
  export default {
    setup() {
      const username = ref('')
      const password = ref('')
      const email = ref('')
      const message = ref('')
      const router = useRouter()
  
      const handleSubmit = () => {
        try {
          const response = axios.post('http://localhost:8000/register', {
            username: username.value,
            password: password.value,
            email: email.value
          })
            // router.push("http://localhost:8000/login")
            // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status === 200) {
          console.log('ユーザー作成成功:', response.data)
          message.value = 'ユーザー作成成功';
          setTimeout(() => {
            router.push('/login');
          }, 2000); // 2秒後にログインページへ遷移
        }
        } catch (error) {
          console.error('ユーザー作成失敗:', error)
          // エラー処理（ユーザーへの通知など）
        }
      }
  
      return {
        username,
        password,
        email,
        message,
        handleSubmit
      }
    }
  }
  </script>