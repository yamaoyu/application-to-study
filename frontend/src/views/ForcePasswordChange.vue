<template>
  <h2 class="mb-5">パスワード変更</h2>
  <BForm @submit.prevent="submitPasswordChange">
    <div class="form-group mt-3">
      <div class="input-group">
        <BFormInput
          v-model="newPassword"
          :type="!showNewPassword ? 'password' : 'text'"
          placeholder="新しいパスワード(必須)"
          :state="passwordValidateResult.valid"
          required
          data-testid="newPassword"
        />
        <button
          class="btn btn-outline-secondary"
          type="button"
          @click="showNewPassword = !showNewPassword"
        >
          <i :class="['bi', showNewPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
        </button>
      </div>
      <div class="feedback-container">
        <BFormInvalidFeedback
          :state="passwordValidateResult.valid"
          data-testid="pass-validate-message"
        >
          {{ passwordValidateResult.message }}
        </BFormInvalidFeedback>
        <BFormValidFeedback
          :state="passwordValidateResult.valid"
          data-testid="valid-password"
        >
          OK
        </BFormValidFeedback>
      </div>
    </div>
    <div class="form-group mt-3">
      <div class="input-group">
        <BFormInput
          v-model="newPasswordCheck"
          :type="!showNewPasswordCheck ? 'password' : 'text'"
          placeholder="新しいパスワード確認(必須)"
          :state="passwordEqualResult.valid"
          required
          data-testid="newPasswordCheck"
        />
        <button
          class="btn btn-outline-secondary"
          type="button"
          @click="showNewPasswordCheck = !showNewPasswordCheck"
        >
          <i
            :class="['bi', showNewPasswordCheck ? 'bi-eye-slash' : 'bi-eye']"
          ></i>
        </button>
      </div>
      <div class="feedback-container">
        <BFormInvalidFeedback
          :state="passwordEqualResult.valid"
          data-testid="pass-equal-invalid"
        >
          パスワードが一致しません
        </BFormInvalidFeedback>
        <BFormValidFeedback
          :state="passwordEqualResult.valid"
          data-testid="pass-equal-valid"
        >
          OK
        </BFormValidFeedback>
      </div>
    </div>
    <button
      type="submit"
      class="btn btn-outline-secondary my-3"
      data-testid="password-change-button"
    >
      変更
    </button>
  </BForm>
  <div class="container d-flex flex-column align-items-center">
    <p
      v-if="message"
      class="col-8 mt-3"
      :class="getResponseAlert(statusCode)"
      data-testid="message"
    >
      {{ message }}
    </p>
  </div>
</template>

<script lang="ts">
import { ref } from "vue";
import {
  BForm,
  BFormInput,
  BFormInvalidFeedback,
  BFormValidFeedback,
} from "bootstrap-vue-next";
import { getResponseAlert } from "./utils/ui";
import {
  useForceChangePassword,
  usePasswordValidation,
} from "./composables/useUserInfo";
import { useAuthStore, useRoleStore } from "@/store/authenticate";
import { useRouter } from "vue-router";

export default {
  components: {
    BForm,
    BFormInput,
    BFormInvalidFeedback,
    BFormValidFeedback,
  },

  setup() {
    const {
      newPassword,
      newPasswordCheck,
      message,
      statusCode,
      changePassword,
    } = useForceChangePassword();
    const showNewPassword = ref<boolean>(false);
    const showNewPasswordCheck = ref<boolean>(false);
    const { passwordValidateResult, passwordEqualResult } =
      usePasswordValidation(newPassword, newPasswordCheck);
    const authStore = useAuthStore();
    const roleStore = useRoleStore();
    const router = useRouter();

    const submitPasswordChange = async () => {
      if (
        !passwordValidateResult.value.valid ||
        !passwordEqualResult.value.valid
      ) {
        return;
      }
      await changePassword();

      if (statusCode.value !== 200) {
        return;
      }
      authStore.clearAuthData();
      roleStore.clearRole();

      await router.replace({
        name: "Login",
        query: {
          message:
            "パスワードを変更しました。新しいパスワードでログインしてください",
        },
      });
    };

    return {
      newPassword,
      newPasswordCheck,
      message,
      statusCode,
      getResponseAlert,
      passwordValidateResult,
      passwordEqualResult,
      showNewPassword,
      showNewPasswordCheck,
      submitPasswordChange,
    };
  },
};
</script>
