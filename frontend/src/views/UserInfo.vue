<template>
  <BForm @submit.prevent="submitNewPassword" class="container d-flex flex-column align-items-center">
    <div class="form-group mt-3 col-8">
      <BFormInput type="password" placeholder="現在のパスワード(必須)" v-model="oldPassword" required/>
    </div>
    <div class="form-group mt-3 col-8">
      <BFormInput type="password" placeholder="新しいパスワード(必須)" v-model="newPassword" :state="isValidPassword.valid" required/>
      <BFormInvalidFeedback :state="isValidPassword.valid">
        {{ isValidPassword.message }}
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="isValidPassword.valid"> OK </BFormValidFeedback>
    </div>
    <div class="form-group mt-3 col-8">
      <BFormInput type="password" placeholder="新しいパスワード確認(必須)" v-model="newPasswordCheck" :state="isEqualPassword" required/>
      <BFormInvalidFeedback :state="isEqualPassword">
        パスワードが一致しません
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="isEqualPassword"> OK </BFormValidFeedback>
      </div>
    <button type="submit" class="btn btn-outline-secondary mt-3">更新</button>
  </BForm>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" class="col-8 mt-3" :class="getResponseAlert(statusCode)">{{ message }}</p>
  </div>
</template>
  
  <script>
  import { ref, computed } from 'vue'
  import axios from 'axios'
  import { getResponseAlert, verifyRefreshToken, commonError, validatePassword, checkPassword } from './lib';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/store/authenticate';
  import { jwtDecode } from 'jwt-decode';
  import { BForm, BFormInput, BFormInvalidFeedback, BFormValidFeedback } from 'bootstrap-vue-next';
  
  export default {
    components: {
      BForm,
      BFormInput,
      BFormInvalidFeedback,
      BFormValidFeedback,
    },

    setup() {
      const oldPassword = ref('')
      const newPassword = ref('')
      const newPasswordCheck = ref('')
      const message = ref('')
      const statusCode = ref()
      const router = useRouter()
      const authStore = useAuthStore()
      const { handleError } = commonError(statusCode, message, router)

      const isValidPassword = computed(() => {
        return validatePassword(newPassword).validate()
      })

      const isEqualPassword = computed(() => {
        return checkPassword(newPassword, newPasswordCheck).validate()
      })

      const changePassword = async() =>{
        // パスワード変更リクエスト送信処理、submitChangePass関数で呼び出される
        const url = process.env.VUE_APP_BACKEND_URL + 'password'
        const response = await axios.put(
          url, 
          {old_password: oldPassword.value, new_password: newPassword.value},
          {headers: {Authorization: authStore.getAuthHeader}}
        )
        if (response.status===200){
          statusCode.value = response.status
          message.value = response.data.message
          oldPassword.value = ''
          newPassword.value = ''
          newPasswordCheck.value = ''
        }
      }

      const submitNewPassword = async() => {
        // 送信ボタンクリック時に実行される
        try {
          await changePassword();
        } catch (error) {
          if (error.response?.status === 401) {
          try {
            // リフレッシュトークンを検証して新しいアクセストークンを取得
            const tokenResponse = await verifyRefreshToken();
            // 新しいアクセストークンをストアに保存
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await changePassword();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          handleError(error)
        }
        }
      }
  
      return {
        oldPassword,
        newPassword,
        newPasswordCheck,
        message,
        statusCode,
        getResponseAlert,
        submitNewPassword,
        isValidPassword,
        isEqualPassword
      }
    }
  }
  </script>