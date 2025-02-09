<template>
  <h3>目標時間の登録</h3>
  <form @submit.prevent="registerTarget">
    <div>
      <label for="date">日付:</label>
      <input type="date" id="date" v-model="date" required>
      <input type="button" value="今日" @click="insertToday">
      <input type="button" value="-1" @click="decreaseOneDay">
      <input type="button" value="+1" @click="increaseOneDay">
    </div>
    <div>
      <label for="TargetTime">目標時間(Hour):</label>
      <select v-model="TargetTime">
        <option v-for="option in timeOptions" :key="option" :value="option">
        {{ option }}
        </option>
      </select>
      <input type="button" value="-0.5" @click="decreaseHalfHour">
      <input type="button" value="+0.5" @click="increaseHalfHour">
      <input type="button" value="-2" @click="decreaseTwoHour">
      <input type="button" value="+2" @click="increaseTwoHour">
    </div>
    <button type="submit">登録</button>
  </form>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { generateTimeOptions, changeDate, changeTime } from "./lib/index";

export default {
  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref("")
    const message = ref("")
    const timeOptions = generateTimeOptions(0.5, 12, 0.5);
    const TargetTime = ref(timeOptions[0]);
    const router = useRouter()
    const authStore = useAuthStore()
    const { insertToday, decreaseOneDay, increaseOneDay } = changeDate(date, message);
    const { increaseHalfHour, decreaseHalfHour, increaseTwoHour, decreaseTwoHour } = changeTime(TargetTime, timeOptions, message);

    const registerTarget = async() =>{
        try {
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
                                          {target_time: Number(TargetTime.value)},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (response.status===201){
            message.value = response.data.message
          }
        } catch (error) {
          // エラー処理（ユーザーへの通知など）
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
                message.value =  "目標時間の登録に失敗しました"
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
      year,
      month,
      day,
      date,
      message,
      timeOptions,
      TargetTime,
      registerTarget,
      insertToday,
      decreaseOneDay,
      increaseOneDay,
      increaseHalfHour,
      decreaseHalfHour,
      increaseTwoHour,
      decreaseTwoHour
    }
  }
}
</script>