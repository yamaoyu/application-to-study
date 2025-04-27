<template>
  <h2 class="mb-5">ユーザー管理メニュー</h2>
  <div class="container col-8 card">
    <h5 class="card-title mt-3 clickable" @click="toggleFormVisibility">パスワード変更</h5>
    <hr class="divider">

    <div class="collapse" :class="{ 'show': isFormVisible }">
      <div class="text-start mt-3">
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="checkbox" id="changePassword" v-model="isPasswordChangeEnabled">
          <label class="form-check-label" for="changePassword">パスワードを変更する</label>
        </div>
      </div>
      
      <BForm @submit.prevent="submitNewPassword">
        <div class="form-group mt-3">
          <div class="input-group">
            <BFormInput :type="!showOldPassword ? 'password':'text'" placeholder="現在のパスワード(必須)" v-model="oldPassword" :disabled="!isPasswordChangeEnabled" required/>
            <button class="btn btn-outline-secondary" type="button" 
                    @click="showOldPassword = !showOldPassword"
                    :disabled="!isPasswordChangeEnabled">
              <i :class="['bi', showOldPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
            </button>
          </div>
        </div>
        <div class="form-group mt-3">
          <div class="input-group">
            <BFormInput :type="!showNewPassword ? 'password':'text'" placeholder="新しいパスワード(必須)" v-model="newPassword" :disabled="!isPasswordChangeEnabled" :state="isValidPassword.valid" required/>
            <button class="btn btn-outline-secondary" type="button"
                    @click="showNewPassword = !showNewPassword"
                    :disabled="!isPasswordChangeEnabled">
              <i :class="['bi', showNewPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
            </button>
          </div>
          <div class="feedback-container">
            <BFormInvalidFeedback :state="isValidPassword.valid">
              {{ isValidPassword.message }}
            </BFormInvalidFeedback>
            <BFormValidFeedback :state="isValidPassword.valid"> OK </BFormValidFeedback>
          </div>
        </div>
        <div class="form-group mt-3">
          <div class="input-group">
            <BFormInput :type="!showNewPasswordCheck ? 'password':'text'" placeholder="新しいパスワード確認(必須)" v-model="newPasswordCheck" :disabled="!isPasswordChangeEnabled" :state="isEqualPassword" required/>
            <button class="btn btn-outline-secondary" type="button"
                    @click="showNewPasswordCheck = !showNewPasswordCheck"
                    :disabled="!isPasswordChangeEnabled">
              <i :class="['bi', showNewPasswordCheck ? 'bi-eye-slash' : 'bi-eye']"></i>
            </button>
          </div>
          <div class="feedback-container">
            <BFormInvalidFeedback :state="isEqualPassword">
              パスワードが一致しません
            </BFormInvalidFeedback>
            <BFormValidFeedback :state="isEqualPassword"> OK </BFormValidFeedback>
          </div>
        </div>
        <button type="submit" class="btn btn-outline-secondary my-3" :disabled="!isPasswordChangeEnabled" >変更</button>
      </BForm>
    </div>
  </div>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" class="col-8 mt-3" :class="getResponseAlert(statusCode)">{{ message }}</p>
  </div>
</template>
  
  <script>
  import { ref, computed, watch } from 'vue'
  import axios from 'axios'
  import { getResponseAlert, verifyRefreshToken, errorWithStatusCode, validatePassword, checkPassword } from './lib';
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
      const isPasswordChangeEnabled = ref(false)
      const isFormVisible = ref(false)
      const showOldPassword = ref(false)
      const showNewPassword = ref(false)
      const showNewPasswordCheck = ref(false)
      const { handleError } = errorWithStatusCode(statusCode, message, router)

      const isValidPassword = computed(() => {
        return validatePassword(newPassword).validate()
      })

      const isEqualPassword = computed(() => {
        return checkPassword(newPassword, newPasswordCheck).validate()
      })

       // フォームの表示/非表示を切り替える
      const toggleFormVisibility = () => {
        isFormVisible.value = !isFormVisible.value
      }

      // パスワード変更オプションが変更されたときに入力をクリア
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
  
      watch(isPasswordChangeEnabled, () => {
        oldPassword.value = ''
        newPassword.value = ''
        newPasswordCheck.value = ''
    })

      return {
        oldPassword,
        newPassword,
        newPasswordCheck,
        message,
        statusCode,
        getResponseAlert,
        submitNewPassword,
        isValidPassword,
        isEqualPassword,
        isPasswordChangeEnabled,
        isFormVisible,
        toggleFormVisibility,
        showOldPassword,
        showNewPassword,
        showNewPasswordCheck
      }
    }
  }
  </script>