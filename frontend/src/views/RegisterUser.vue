<template>
  <nav class="navbar navbar-expand-lg bd-navbar fixed-top bg-dark navbar-dark">
    <div class="container-fluid">
      <ul class="navbar-nav ms-auto me-2" style="color: white;">
        <li class="nav-item">
          <router-link class="nav-link fs-5 py-1" to="/login">LOGIN</router-link>
        </li>
      </ul>
    </div>
  </nav>
  <h2>ユーザー登録</h2>
  <BForm @submit.prevent="submit" class="container d-flex flex-column align-items-center">
    <div class="form-group mt-3 col-8">
      <BFormInput placeholder="ユーザー名(必須)" v-model="username" :state="usernameValidateResult.valid" data-testid="username" required/>
      <BFormInvalidFeedback :state="usernameValidateResult.valid">
        {{ usernameValidateResult.message }}
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="usernameValidateResult.valid"> OK </BFormValidFeedback>
    </div>
    <div class="form-group mt-3 col-8">
      <div class="input-group">
        <BFormInput :type="!showPassword ? 'password':'text'" placeholder="パスワード(必須)" v-model="password" :state="passwordValidateResult.valid" data-testid="password" required/>
        <button class="btn btn-outline-secondary" type="button" @click="showPassword = !showPassword">
          <i :class="['bi', showPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
        </button>
      </div>
      <div class="feedback-container">
        <BFormInvalidFeedback :state="passwordValidateResult.valid">
          {{ passwordValidateResult.message }}
        </BFormInvalidFeedback>
        <BFormValidFeedback :state="passwordValidateResult.valid"> OK </BFormValidFeedback>
      </div>
    </div>
    <div class="form-group mt-3 col-8">
      <div class="input-group">
        <BFormInput :type="!showPasswordCheck ? 'password':'text'" placeholder="パスワード確認(必須)" v-model="passwordCheck" :state="passwordEqualResult.valid" data-testid="passwordCheck" required/>
        <button class="btn btn-outline-secondary" type="button" @click="showPasswordCheck = !showPasswordCheck">
          <i :class="['bi', showPasswordCheck ? 'bi-eye-slash' : 'bi-eye']"></i>
        </button>
      </div>
      <div class="feedback-container">
        <BFormInvalidFeedback :state="passwordEqualResult.valid">
          {{ passwordEqualResult.message }}
        </BFormInvalidFeedback>
        <BFormValidFeedback :state="passwordEqualResult.valid"> OK </BFormValidFeedback>
      </div>
    </div>
    <div class="form-group mt-3 col-8" v-if="showMailForm">
      <BFormInput placeholder="メールアドレス(任意)" type="email" v-model="email" :state="emailValidateResult.valid" data-testid="email"/>
      <BFormInvalidFeedback :state="emailValidateResult.valid">
        {{ emailValidateResult.message }}
      </BFormInvalidFeedback>
      <BFormValidFeedback :state="emailValidateResult.valid"> OK </BFormValidFeedback>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3" data-testid="register-user-button">登録</button>
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
  import { getResponseAlert } from './lib';
  import { BForm, BFormInput, BFormInvalidFeedback, BFormValidFeedback } from 'bootstrap-vue-next';
  import { validateUsername, validatePassword, checkPassword, validateEmail } from './utils/userValidation';
  import { useRegisterUser } from './composables/userRegisterUser';

  export default {
    components: {
      BForm,
      BFormInput,
      BFormInvalidFeedback,
      BFormValidFeedback
    },

    setup() {
      const showPassword = ref(false);
      const showPasswordCheck = ref(false);
      const showMailForm = import.meta.env.VITE_MAIL_FORM === 'true';
      const {
        username,
        password,
        passwordCheck,
        email,
        message,
        statusCode,
        submit
      } = useRegisterUser();

      const usernameValidateResult = computed(() => {
        return validateUsername(username.value);
      });

      const passwordValidateResult = computed(() => {
        return validatePassword(password.value);
      });

      const passwordEqualResult = computed(() => {
        return checkPassword(password.value, passwordCheck.value);
      });

      const emailValidateResult = computed(() => {
        return validateEmail(email.value);
      });
  
      return {
        username,
        password,
        passwordCheck,
        email,
        message,
        statusCode,
        getResponseAlert,
        usernameValidateResult,
        passwordValidateResult,
        passwordEqualResult,
        emailValidateResult,
        showPassword,
        showPasswordCheck,
        showMailForm,
        submit
      }
    }
  }
  </script>
