<template>
  <h3>活動時間の登録</h3>
  <form @submit.prevent="registerActual">
    <div>
      <label for="date">日付:</label>
      <input type="date" id="date" v-model="date" required>
      <input type="button" value="今日" @click="insertToday">
      <input type="button" value="-1" @click="decreaseOneDay">
      <input type="button" value="+1" @click="increaseOneDay">
    </div>
    <div>
      <label for="ActualTime">活動時間:</label>
      <select v-model="ActualTime">
        <option v-for="option in timeOptions" :key="option" :value="option">
        {{ option }}
        </option>
      </select>
      <input type="button" value="-0.5" @click="decreaseHalfHour">
      <input type="button" value="+0.5" @click="increaseHalfHour">
    </div>
    <button type="submit">登録</button>
  </form>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { generateTimeOptions } from "./lib/index";
import { useAuthStore } from '@/store/authenticate';
import { getToday, getNextDay, getPreviousDay } from './lib/dateUtils';

export default {
  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref("")
    const message = ref("")
    const timeOptions = generateTimeOptions(0.0, 12, 0.5);
    const ActualTime = ref(timeOptions[0])
    const router = useRouter()
    const authStore = useAuthStore()

    const insertToday = async() =>{
      date.value = getToday();
    }

    const decreaseOneDay = async() => {
      if (date.value) {
        date.value = getPreviousDay(date.value);
        message.value = ""
      } else {
        message.value = "日付が指定されていません"
      }
    }

    const increaseOneDay = async() => {
      if (date.value !== '') {
        date.value = getNextDay(date.value);
        message.value = ""
      } else{
        message.value = "日付が指定されていません"
      }
    }

    const increaseHalfHour = async() => {
      const currentIndex = timeOptions.indexOf(ActualTime.value)
      if (currentIndex < timeOptions.length - 1) {
        ActualTime.value = timeOptions[currentIndex + 1]
      }
    }

    const decreaseHalfHour = async() => {
      const currentIndex = timeOptions.indexOf(ActualTime.value)
      if (currentIndex > 0) {
        ActualTime.value = timeOptions[currentIndex - 1]
      }
    }

    const registerActual = async() =>{
        try {
          // 日付から年月日を取得
          const dateParts = date.value.split('-');
          year.value = dateParts[0];
          month.value = dateParts[1];
          day.value = dateParts[2];
          // 月と日が一桁の場合、表記を変更 例)09→9
          month.value = parseInt(month.value, 10);
          day.value = parseInt(day.value, 10);
          const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value + '/' + month.value + '/' + day.value +  '/actual';
          const response = await axios.put(url, 
                                          {actual_time: Number(ActualTime.value)},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (response.status===200){
            message.value = response.data.message
          }
        } catch (error) {
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
      year,
      month,
      day,
      date,
      message,
      timeOptions,
      ActualTime,
      registerActual,
      insertToday,
      decreaseOneDay,
      increaseOneDay,
      increaseHalfHour,
      decreaseHalfHour
    }
  }
}
</script>