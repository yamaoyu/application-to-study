<template>
  <h3>活動時間の登録</h3>
  <form @submit.prevent="registerActual">
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
        <span class="input-group-text">実績</span>
        <input
          type="number"
          v-model="actualTime"
          class="form-control col-2 text-center"
          min="0.0"
          max="12"
          step="0.5"
          placeholder="活動時間(Hour)"
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
    <b-modal v-model="isModalShow" title="活動時間登録成功" ok-title="はい" cancel-title="いいえ" @ok="finishActivity()">
      <p class="my-4">{{ date }}の活動を終了しますか？</p>
    </b-modal>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { changeDate, changeTime, getResponseAlert, useActivityFinish, getToday } from "./lib/index";
import { useAuthStore } from '@/store/authenticate';
import { BModal } from 'bootstrap-vue-next';

export default {
  components: {
    BModal,
  },

  setup() {
    const date = ref(getToday()); // 今日の日付を取得
    const message = ref("")
    const actualTime = ref(0)
    const router = useRouter()
    const authStore = useAuthStore()
    const statusCode = ref()
    const { increaseDay } = changeDate(date, message);
    const { decreaseHour, increaseHour } = changeTime(actualTime, message);
    const { finishActivity } = useActivityFinish(date, message, router, authStore);
    const isMinHour = computed(() => actualTime.value <= 0.0);
    const isMaxHour = computed(() => actualTime.value >= 12.0);
    const isModalShow = ref(false);

    const registerActual = async() =>{
        try {
          // 日付から年月日を取得
          const dateParts = date.value.split('-');
          const year = dateParts[0];
          // 月と日が一桁の場合、表記を変更 例)09→9
          const month = parseInt(dateParts[1], 10);
          const day = parseInt(dateParts[2], 10);
          const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day +  '/actual';
          const response = await axios.put(url, 
                                          {actual_time: Number(actualTime.value)},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          statusCode.value = response.status
          if (response.status===200){
            message.value = response.data.message
            isModalShow.value = true;
          }
        } catch (error) {
          statusCode.value = error.response.status
          if (error.response){
          switch (error.response.status){
            case 401:
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
              break;
            case 422:
              message.value = error.response.data.detail;
              break;
            case 500:
              message.value =  "活動時間の登録に失敗しました"
              break;
            default:
              message.value = error.response.data.detail;}
          } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }

    return {
      date,
      message,
      actualTime,
      registerActual,
      getResponseAlert,
      statusCode,
      finishActivity,
      increaseDay,
      increaseHour,
      decreaseHour,
      isMinHour,
      isMaxHour,
      isModalShow
    }
  }
}
</script>