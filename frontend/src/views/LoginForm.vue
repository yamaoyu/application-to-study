<template>
  <h3>ログイン</h3>
  <form 
    class="container d-flex flex-column align-items-center" 
    data-testid="login-form"
    @submit.prevent="userLogin" 
  >
    <div class="mt-3 col-6">
      <input v-model="username" type="text" placeholder="username" class="form-control" data-testid="username" required>
    </div>
    <div class="mt-3 col-6">
      <div class="input-group">
        <input v-model="password" :type="inputType" placeholder="password" class="form-control" data-testid="password" required>
        <button 
          class="btn btn-outline-secondary" type="button"
          @click="showPassword = !showPassword">
          <i :class="['bi', showPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
        </button>
      </div>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3" data-testid="login-button">ログイン</button>
  </form>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" :class="getResponseAlert(statusCode)" class="mt-3 col-8" data-testid="message">{{ message }}</p>
  </div>
  <div class="mt-3">
    <router-link to="/register/user">登録はこちら</router-link>
  </div>
</template>
  
  <script lang="ts">
  import { ref, onMounted, computed } from 'vue';
  import { useRoute } from 'vue-router';
  import { getResponseAlert } from './utils/ui';
  import { useLogin } from './composables/useAuth';

  export default {
    setup() {
      const route = useRoute();
      const showPassword = ref<boolean>(false);
      const { username, password, message, statusCode, router, userLogin } = useLogin();

      const inputType = computed(() =>
        showPassword.value ? 'text' : 'password'
      );

      onMounted(() => {
      if (typeof route.query.message === 'string') {
        message.value = route.query.message;
        // オプション: メッセージを表示後、URLからパラメータを削除
        router.replace({ query: {} })
        }
      })

      return {
        username,
        password,
        message,
        statusCode,
        getResponseAlert,
        userLogin,
        showPassword,
        inputType
      }
    }
  }
  </script>