<template>
  <h2>ユーザー登録</h2>
  <BForm @submit.prevent="createUser" class="container d-flex flex-column align-items-center">
    <div class="form-group mt-3 col-8">
      <BFormInput placeholder="username(必須)" v-model="username" :state="validateUsername" required/>
      <BFormInvalidFeedback :state="validateUsername">
        ユーザー名は3文字以上16文字以下にして下さい
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="validateUsername"> OK </BFormValidFeedback>
    </div>
    <div class="form-group mt-3 col-8">
      <BFormInput type="password" placeholder="password(必須)" v-model="password" :state="validatePassword" required/>
      <BFormInvalidFeedback :state="validatePassword">
        パスワードは8文字以上16文字以下にして下さい
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="validatePassword"> OK </BFormValidFeedback>
    </div>
    <div class="form-group mt-3 col-8">
      <BFormInput placeholder="email(任意)" v-model="email" :state="validateEmail" />
      <BFormInvalidFeedback :state="validateEmail">
        メールアドレスの形式で入力して下さい
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="validateEmail"> OK </BFormValidFeedback>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3">登録</button>
  </BForm>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" :class="getResponseAlert(statusCode)" class="mt-3 col-8">{{ message }}</p>
  </div>
  <div class="mt-3">
    <router-link to="/login">ログインはこちら</router-link>
  </div>
</template>
  
  <script>
  import { ref, computed } from 'vue'
  import axios from 'axios'
  import { getResponseAlert } from './lib';
  import { BForm, BFormInput, BFormInvalidFeedback, BFormValidFeedback } from 'bootstrap-vue-next';
  
  export default {
    components: {
      BForm,
      BFormInput,
      BFormInvalidFeedback,
      BFormValidFeedback
    },

    setup() {
      const username = ref('')
      const password = ref('')
      const email = ref('')
      const message = ref('')
      const statusCode = ref()

      const validateUsername = computed(() => {
        if (username.value.length === 0) {
          return null
        }
        return username.value.length >= 3 && username.value.length <= 16})

      const validatePassword = computed(() => {
        if (password.value.length === 0) {
          return null
        }
        return password.value.length >= 8 && password.value.length <= 16})

      const validateEmail = computed(() => {
        if (email.value.length === 0) {
          return null
        }
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email.value);
      })
  
      const createUser = async() => {
        try {
          const url = process.env.VUE_APP_BACKEND_URL + 'users'
          const response = await axios.post(
            url, 
            {
              username: username.value,
              password: password.value,
              email: email.value
            }
          )
          if (response.status===201){
            statusCode.value = response.status;
            message.value = response.data.message;
          }
        } catch (error) {
          statusCode.value = error.response.status;
          if (error.response){
            switch (error.response.status){
              case 422:
                message.value = error.response.data.detail;
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
        statusCode,
        createUser,
        getResponseAlert,
        validateUsername,
        validatePassword,
        validateEmail
      }
    }
  }
  </script>