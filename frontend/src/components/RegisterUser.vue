<template>
    <form @submit.prevent="CreateUser">
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
    <p v-if="message" class="message">{{ message }}</p>
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
  
      const CreateUser = async() => {
        try {
          const response = await axios.post('http://localhost:8000/register', {
            username: username.value,
            password: password.value,
            email: email.value
          })
            // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===200){
            router.push({
            path:'/login', 
            query : { message:response.data.message }})
          }
        } catch (error) {
          // エラー処理（ユーザーへの通知など）
          if (error.response.status!==500){
            message.value = error.response.data.detail;
          }else{
            message.value = "ユーザー作成に失敗しました";
          }
        }
      }
  
      return {
        username,
        password,
        email,
        message,
        CreateUser
      }
    }
  }
  </script>