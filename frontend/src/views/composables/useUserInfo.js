import { ref, computed } from "vue";
import { updatePassword } from "../api/user";
import { parseError } from "../utils/error";
  import { validateUsername, validatePassword, checkPassword, validateEmail } from '../utils/userValidation';

export const useChangePassword = () => {
  const oldPassword = ref('');
  const newPassword = ref('');
  const newPasswordCheck = ref('');
  const message = ref('');
  const statusCode = ref();

  const changePassword = async() => {
    try {
      const res = await updatePassword(oldPassword.value, newPassword.value);
      if (res.status===200){
        statusCode.value = res.status
        message.value = res.data.message
        oldPassword.value = ''
        newPassword.value = ''
        newPasswordCheck.value = ''
      }
    } catch(error) {
      message.value = parseError(error, "パスワードの変更に失敗しました");
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

export const useUserInfoCheck = (username, password, passwordCheck, email) => {
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
    usernameValidateResult,
    passwordValidateResult,
    passwordEqualResult,
    emailValidateResult
  }
};
