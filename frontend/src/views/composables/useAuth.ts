import { ref } from 'vue';
import { login, logout } from '../api/auth';
import { parseError } from '../utils/error';
import { jwtDecode } from 'jwt-decode';
import { useRouter } from 'vue-router';
import { useAuthStore, useRoleStore } from '@/store/authenticate';
import axios from 'axios';
import { AuthTokenResponse } from '../types/auth';

export const setAuthDataFromToken = (
  authStore: ReturnType<typeof useAuthStore>,
  response: AuthTokenResponse
) => {
  const decoded = jwtDecode(response.access_token);

  if (!decoded.exp) {
    throw new Error("トークンの有効期限がありません");
  }

  authStore.setAuthData(response.access_token, response.token_type, decoded.exp);
};


export const useLogin = () => {
  const username = ref<string>("");
  const password = ref<string>("");
  const message = ref<string>("");
  const statusCode = ref<number | null>(null);
  const router = useRouter();
  const authStore = useAuthStore();
  const roleStore = useRoleStore();

  const validateForm = () => {
    if (!username.value) return 'ユーザー名を入力してください'
    if (!password.value) return 'パスワードを入力してください'
    return null
  };

  const userLogin = async () => {
    const error = validateForm()
    if (error) {
      message.value = error
      return
    }

    try {
      const response = await login(username.value, password.value);
      await setAuthDataFromToken(authStore, response.data)

      roleStore.setRole(response.data.role)

      if (authStore.getRedirectPath) {
        router.push({ path: authStore.getRedirectPath })
      } else {
        router.push({ path: "/home" })
      }
    } catch (error) {
      message.value = parseError(error, "ログインに失敗しました")
      if (axios.isAxiosError(error)) {
        statusCode.value = error.response?.status || null;
      } else {
        statusCode.value = null;
      }
    }
  };

  return {
    username,
    password,
    message,
    statusCode,
    router,
    userLogin
  }
};

export const useLogout = () => {
  const message = ref("");
  const router = useRouter();
  const authStore = useAuthStore();
  const roleStore = useRoleStore();

  const userLogout = async () => {
    try {
      await logout();
      authStore.clearAuthData();
      roleStore.clearRole();
      router.push(
        {
          path: "/login",
          query: { message: "ログアウトしました" }
        })
    } catch (error) {
      message.value = parseError(error, "ログアウトに失敗しました");
    }
  }

  return {
    message,
    roleStore,
    userLogout
  }
};
