<template>
  <h3>ログイン</h3>
  <form @submit.prevent="userLogin" class="container d-flex flex-column align-items-center" data-testid="login-form">
    <div class="mt-3 col-6">
      <input type="text" placeholder="username" class="form-control" v-model="username" data-testid="username" required>
    </div>
    <div class="mt-3 col-6">
      <div class="input-group">
        <input :type="inputType" placeholder="password" class="form-control" v-model="password" data-testid="password" required>
        <button class="btn btn-outline-secondary" type="button"
                    @click="showPassword = !showPassword">
          <i :class="['bi', showPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
        </button>
      </div>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3" data-testid="login-button">ログイン</button>
  </form>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" :class="getResponseAlert(statusCode)" class="mt-3 col-8">{{ message }}</p>
  </div>
  <div class="mt-3">
    <router-link to="/register/user">登録はこちら</router-link>
  </div>
</template>
  
  <script>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useAuthStore, useRoleStore } from '@/store/authenticate';
  import { getResponseAlert } from './lib';
  import { useLogin } from './composables/useLogin';

  export default {
    setup() {
      const router =  useRouter();
      const route = useRoute();
      const showPassword = ref(false);
      const authStore = useAuthStore();
      const roleStore = useRoleStore();
      const { username, password, message, statusCode, userLogin } =
          useLogin(router, authStore, roleStore);

      const inputType = computed(() =>
        showPassword.value ? 'text' : 'password'
      );

      onMounted(() => {
      if (route.query.message) {
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