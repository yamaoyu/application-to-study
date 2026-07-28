import { ref } from 'vue'
import { createUser } from '../api/user'
import { parseError } from '../utils/error'
import axios from 'axios';

export const useRegisterUser = () => {
  const username = ref<string>('');
  const password = ref<string>('');
  const passwordCheck = ref<string>('');
  const email = ref<string>('');
  const message = ref<string>('');
  const statusCode = ref<number | null>(null);

  const submit = async () => {
    try {
      const res = await createUser(username.value, password.value, email.value ?? '')

      message.value = `${username.value}を作成しました`;
      statusCode.value = res.status

    } catch (error) {
      message.value = parseError(error, "ユーザー作成に失敗しました");
      if (axios.isAxiosError(error)) {
        statusCode.value = error.response?.status || null;
      } else {
        statusCode.value = null;
      }
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