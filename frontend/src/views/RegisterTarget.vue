<template>
  <h3>目標時間の登録</h3>
  <form @submit.prevent="registerTarget">
    <div class="container col-8 d-flex justify-content-center mt-3">
      <div class="input-group">
        <span class="input-group-text">日付</span>
        <input
          type="date"
          v-model="date"
          class="form-control col-2"
          min="2024-01-01"
        />
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseDay(-1)"
          >
          前日
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseDay(1)"
          >
          翌日
        </button>
      </div>
    </div>
    <div class="container col-8 d-flex justify-content-center mt-3">
      <div class="input-group">
        <span class="input-group-text">目標</span>
        <input
          type="number"
          v-model="targetTime"
          class="form-control col-2 text-center"
          min="0.5"
          max="12"
          step="0.5"
          placeholder="目標時間(Hour)"
        />
        <span class="input-group-text small">時間</span>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="decreaseHour(1)"
          :disabled="isMinHour"
          >
          -1
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseHour(1)"
          :disabled="isMaxHour"
          >
          +1
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="decreaseHour(3)"
          :disabled="isMinHour"
          >
          -3
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseHour(3)"
          :disabled="isMaxHour"
          >
          +3
        </button>
      </div>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3">登録</button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 col-8" :class="getResponseAlert(statusCode)">{{ message }}</p>
  </div>
  <div>
    <b-modal v-model="isModalShow" title="目標時間登録成功" ok-title="はい" cancel-title="いいえ" @ok="router.push('/register/actual')">
      <p class="my-4">活動時間登録ページに移動しますか?</p>
    </b-modal>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { changeDate, changeTime, getResponseAlert, getToday, verfiyRefreshToken, commonError } from "./lib/index";
import { BModal } from 'bootstrap-vue-next';
import { jwtDecode } from 'jwt-decode';

export default {
  components: {
    BModal
  },

  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref(getToday()); // 今日の日付を取得
    const message = ref("")
    const targetTime = ref(0.5);
    const statusCode = ref()
    const isModalShow = ref(false);
    const router = useRouter()
    const authStore = useAuthStore()
    const { increaseDay } = changeDate(date, message);
    const { increaseHour, decreaseHour } = changeTime(targetTime, message);
    const isMinHour = computed(() => targetTime.value <= 0.5);
    const isMaxHour = computed(() => targetTime.value >= 12.0);
    const { handleError } = commonError(statusCode, message, router);

    const submitTarget = async() =>{
      // 日付から年月日を取得
      const dateParts = date.value.split('-');
      year.value = dateParts[0];
      month.value = dateParts[1];
      day.value = dateParts[2];
      // 月と日が一桁の場合、表記を変更 例)09→9
      month.value = parseInt(month.value, 10);
      day.value = parseInt(day.value, 10);
      const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value + '/' + month.value + '/' + day.value + '/target';
      const response = await axios.post(url, 
                                      {target_time: Number(targetTime.value)},
                                      {headers: {Authorization: authStore.getAuthHeader}})
      statusCode.value = response.status
      if (response.status===201){
        isModalShow.value = true;
        message.value = response.data.message
      }
      }

    const registerTarget = async() =>{
        try {
          await submitTarget();
        } catch (error) {
          if (error.response?.status === 401) {
            try {
              // リフレッシュトークンを検証して新しいアクセストークンを取得
              const tokenResponse = await verfiyRefreshToken();
              // 新しいアクセストークンをストアに保存
              await authStore.setAuthData(
              tokenResponse.data.access_token,
              tokenResponse.data.token_type,
              jwtDecode(tokenResponse.data.access_token).exp)
              // 再度リクエストを送信
              await submitTarget();
            } catch (refreshError) {
              router.push({
                path: "/login",
                query: { message: "再度ログインしてください" }
              });
            }            
          } else {
            handleError(error)
          }
        }
      }

    return {
      router,
      year,
      month,
      day,
      date,
      message,
      targetTime,
      statusCode,
      isModalShow,
      registerTarget,
      getResponseAlert,
      increaseDay,
      increaseHour,
      decreaseHour,
      isMinHour,
      isMaxHour
    }
  }
}
</script>