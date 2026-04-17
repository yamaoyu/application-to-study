import { ref } from 'vue'
import { createUser } from '../api/user'
import { parseError } from '../utils/error'

export const useRegisterUser = () => {
  const username = ref('');
  const password = ref('');
  const passwordCheck = ref('');
  const email = ref('');
  const message = ref('');
  const statusCode = ref(null);

  const submit = async () => {
    try {
      const res = await createUser({
        username: username.value,
        password: password.value,
        email: email.value ?? ''
      })

      if (res.status === 201) {
        message.value = res.data.message
        statusCode.value = res.status
      }

    } catch (error) {
      message.value = parseError(error, "ユーザー作成に失敗しました")
      statusCode.value = error.response?.status ?? null
    }
  }

  return {
    username,
    password,
    passwordCheck,
    email,
    message,
    statusCode,
    submit
  }
};