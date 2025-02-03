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
      <input type="button" value="-2" @click="decreaseTwoHour">
      <input type="button" value="+2" @click="increaseTwoHour">
    </div>
    <button type="submit">登録</button>
  </form>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <form v-if="isRegistered" @submit.prevent="finishActivity">
    <div>
      <label for="finishActivity">このまま{{ date }}の活動を終了しますか？</label>
      <input type="button" value="はい" @click="finishActivity">
    </div>
  </form>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { generateTimeOptions, changeDate, changeTime, useActivityFinish } from "./lib/index";
import { useAuthStore } from '@/store/authenticate';

export default {
  setup() {
    const isRegistered = ref(false);
    const date = ref("")
    const message = ref("")
    const timeOptions = generateTimeOptions(0.0, 12, 0.5);
    const ActualTime = ref(timeOptions[0])
    const router = useRouter()
    const authStore = useAuthStore()
    const { insertToday, decreaseOneDay, increaseOneDay } = changeDate(date, message);
    const { decreaseHalfHour, increaseHalfHour, increaseTwoHour, decreaseTwoHour } = changeTime(ActualTime, timeOptions, message);
    const { finishActivity } = useActivityFinish(date, message, router, authStore);

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
                                          {actual_time: Number(ActualTime.value)},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (response.status===200){
            message.value = response.data.message
            isRegistered.value = true;
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
      isRegistered,
      date,
      message,
      timeOptions,
      ActualTime,
      registerActual,
      finishActivity,
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