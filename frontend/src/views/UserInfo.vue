<template>
  <h2 class="mb-5">ユーザー管理メニュー</h2>
  <div class="container col-8 card">
    <h5 class="card-title mt-3 clickable" @click="isFormVisible = !isFormVisible">
      パスワード変更
      <span v-if="isFormVisible" class="ms-2">▲</span>
      <span v-else class="ms-2">▼</span>
    </h5>
    <hr class="divider">

    <div class="collapse" :class="{ 'show': isFormVisible }">
      <div class="text-start mt-3">
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="checkbox" v-model="isPasswordChangeEnabled" data-testid="isPasswordChangeEnabled">
          <label class="form-check-label" for="changePassword">パスワードを変更する</label>
        </div>
      </div>
      
      <BForm @submit.prevent="changePassword">
        <div class="form-group mt-3">
          <div class="input-group">
            <BFormInput :type="!showOldPassword ? 'password':'text'" placeholder="現在のパスワード(必須)" v-model="oldPassword" :disabled="!isPasswordChangeEnabled" required data-testid="oldPassword"/>
            <button class="btn btn-outline-secondary" type="button" 
                    @click="showOldPassword = !showOldPassword"
                    :disabled="!isPasswordChangeEnabled">
              <i :class="['bi', showOldPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
            </button>
          </div>
        </div>
        <div class="form-group mt-3">
          <div class="input-group">
            <BFormInput :type="!showNewPassword ? 'password':'text'" placeholder="新しいパスワード(必須)" v-model="newPassword" :disabled="!isPasswordChangeEnabled" :state="passwordValidateResult.valid" required data-testid="newPassword"/>
            <button class="btn btn-outline-secondary" type="button"
                    @click="showNewPassword = !showNewPassword"
                    :disabled="!isPasswordChangeEnabled">
              <i :class="['bi', showNewPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
            </button>
          </div>
          <div class="feedback-container">
            <BFormInvalidFeedback :state="passwordValidateResult.valid">
              {{ passwordValidateResult.message }}
            </BFormInvalidFeedback>
            <BFormValidFeedback :state="passwordValidateResult.valid"> OK </BFormValidFeedback>
          </div>
        </div>
        <div class="form-group mt-3">
          <div class="input-group">
            <BFormInput :type="!showNewPasswordCheck ? 'password':'text'" placeholder="新しいパスワード確認(必須)" v-model="newPasswordCheck" :disabled="!isPasswordChangeEnabled" :state="passwordEqualResult.valid" required data-testid="newPasswordCheck"/>
            <button class="btn btn-outline-secondary" type="button"
                    @click="showNewPasswordCheck = !showNewPasswordCheck"
                    :disabled="!isPasswordChangeEnabled">
              <i :class="['bi', showNewPasswordCheck ? 'bi-eye-slash' : 'bi-eye']"></i>
            </button>
          </div>
          <div class="feedback-container">
            <BFormInvalidFeedback :state="passwordEqualResult.valid">
              パスワードが一致しません
            </BFormInvalidFeedback>
            <BFormValidFeedback :state="passwordEqualResult.valid"> OK </BFormValidFeedback>
          </div>
        </div>
        <button type="submit" class="btn btn-outline-secondary my-3" :disabled="!isPasswordChangeEnabled" data-testid="password-change-button">変更</button>
      </BForm>
    </div>
  </div>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" class="col-8 mt-3" :class="getResponseAlert(statusCode)">{{ message }}</p>
  </div>
</template>
  
<script>
import { ref, watch } from 'vue'
import { BForm, BFormInput, BFormInvalidFeedback, BFormValidFeedback } from 'bootstrap-vue-next';
import { getResponseAlert } from './utils/ui';
import { useChangePassword, useUserInfoCheck } from './composables/useUserInfo';

export default {
  components: {
    BForm,
    BFormInput,
    BFormInvalidFeedback,
    BFormValidFeedback,
  },

  setup() {
    const { oldPassword, newPassword, newPasswordCheck, message, statusCode, changePassword } = useChangePassword();
    const isPasswordChangeEnabled = ref(false);
    const isFormVisible = ref(false);
    const showOldPassword = ref(false);
    const showNewPassword = ref(false);
    const showNewPasswordCheck = ref(false);
    const { passwordValidateResult, passwordEqualResult } = useUserInfoCheck('', newPassword, newPasswordCheck, '');

    watch(isPasswordChangeEnabled, () => {
      oldPassword.value = ''
      newPassword.value = ''
      newPasswordCheck.value = ''
    });

    return {
      oldPassword,
      newPassword,
      newPasswordCheck,
      message,
      statusCode,
      getResponseAlert,
      passwordValidateResult,
      passwordEqualResult,
      isPasswordChangeEnabled,
      isFormVisible,
      showOldPassword,
      showNewPassword,
      showNewPasswordCheck,
      changePassword
    }
  }
}
</script>
