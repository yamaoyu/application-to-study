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
  <div>
    <router-link to="/login">ログインはこちら</router-link>
  </div>
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
          const url = process.env.VUE_APP_BACKEND_URL + '/users'
          const response = await axios.post(url, {
            username: username.value,
            password: password.value,
            email: email.value
          })
          if (response.status===201){
            router.push({
            path:'/login', 
            query : { message:response.data.message }})
          }
        } catch (error) {
          if (error.response){
            switch (error.response.status){
              case 422:
                message.value = error.response.data.error;
                break;
              case 500:
                message.value =  "ユーザー作成に失敗しました"
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
        email,
        message,
        CreateUser
      }
    }
  }
  </script>