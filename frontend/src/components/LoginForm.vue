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
      <button type="submit">ログイン</button>
    </form>
  </template>
  
  <script>
  import { ref } from 'vue'
  import axios from 'axios'
  // import { useRouter } from 'vue-router';
  
  export default {
    setup() {
      const username = ref('')
      const password = ref('')
      const email = ref('')
      // const router = useRouter()
  
      const handleSubmit = () => {
        try {
          const response = axios.post('http://localhost:8000/login', {
            username: username.value,
            password: password.value,
            email: email.value
          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          console.log('ログイン成功:', response.data)
        } catch (error) {
          console.error('ユーザー作成失敗:', error)
          // エラー処理（ユーザーへの通知など）
        }
      }
  
      return {
        username,
        password,
        handleSubmit
      }
    }
  }
  </script>