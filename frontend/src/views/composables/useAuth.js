import { ref } from 'vue';
import { login, logout } from '../api/auth';
import { parseError } from '../utils/error';
import { jwtDecode } from 'jwt-decode';
import { useRouter } from 'vue-router';
import { useAuthStore, useRoleStore } from '@/store/authenticate';


export const useLogin = () => {
  const username = ref("");
  const password = ref("");
  const message = ref("");
  const statusCode = ref(null);
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
      if (response.status === 200) {
        authStore.setAuthData(
        response.data.access_token,
        response.data.token_type,
        jwtDecode(response.data.access_token).exp
        )

        roleStore.setRole(response.data.role)

        if (authStore.getRedirectPath) {
          router.push({ path: authStore.getRedirectPath })
        } else {
          router.push({ path: "/home" })
        }
      }
    } catch (error) {
      message.value = parseError(error, "ログインに失敗しました")
      statusCode.value = error.response?.status ?? null
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

  const userLogout = async() => {
    try {
      const res = await logout();
      if (res.status===200){
        authStore.clearAuthData();
        roleStore.clearRole();
        router.push(
                { path : "/login",
                  query : {message:"ログアウトしました"}
                })
      }
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
