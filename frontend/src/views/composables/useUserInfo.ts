import { ref, computed, type Ref } from "vue";
import { updatePassword } from "../api/user";
import { parseError } from "../utils/error";
import { validateUsername, validatePassword, checkPassword, validateEmail } from '../utils/userValidation';
import axios from "axios";

export const useChangePassword = () => {
  const oldPassword = ref<string>('');
  const newPassword = ref<string>('');
  const newPasswordCheck = ref<string>('');
  const message = ref<string>('');
  const statusCode = ref<number | null>(null);

  const changePassword = async () => {
    try {
      const res = await updatePassword(oldPassword.value, newPassword.value);
      statusCode.value = res.status
      message.value = "パスワードの変更に成功しました"
      oldPassword.value = ''
      newPassword.value = ''
      newPasswordCheck.value = ''
    } catch (error: unknown) {
      message.value = parseError(error, "パスワードの変更に失敗しました");
      if (axios.isAxiosError(error)) {
        statusCode.value = error.response?.status || null;
      } else {
        statusCode.value = null;
      }
    }
  }

  return {
    oldPassword,
    newPassword,
    newPasswordCheck,
    message,
    statusCode,
    changePassword
  }
};

export const useUsernameValidation = (username: Ref<string>) => {
  const usernameValidateResult = computed(() => validateUsername(username.value));
  return {
    usernameValidateResult
  };
};

export const usePasswordValidation = (password: Ref<string>, passwordCheck: Ref<string>) => {
  const passwordValidateResult = computed(() => validatePassword(password.value));

  const passwordEqualResult = computed(() => checkPassword(password.value, passwordCheck.value));
  return {
    passwordValidateResult,
    passwordEqualResult
  }
}

export const useEmailValidation = (email: Ref<string>) => {
  const emailValidateResult = computed(() => validateEmail(email.value));
  return {
    emailValidateResult
  };
}
