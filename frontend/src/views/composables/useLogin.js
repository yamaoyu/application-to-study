import { ref } from 'vue';
import { login } from '../api/login';
import { parseError } from '../utils/error';
import { jwtDecode } from 'jwt-decode';

export const useLogin = (router, authStore, roleStore) => {
  const username = ref("");
  const password = ref("");
  const message = ref("");
  const statusCode = ref(null);

  const validateForm = () => {
    if (!username.value) return 'ユーザー名を入力してください'
    if (!password.value) return 'パスワードを入力してください'
    return null
  };

  const handleLoginSuccess = (response) => {
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
  };

  const userLogin = async () => {
    const error = validateForm()
    if (error) {
      message.value = error
      return
    }

    try {
      const response = await login(username.value, password.value)
      if (response.status === 200) {
        handleLoginSuccess(response)
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
    userLogin
  }
}