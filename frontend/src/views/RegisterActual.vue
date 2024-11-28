<template>
  <h3>活動時間の登録</h3>
  <form @submit.prevent="RegisterActual">
    <div>
      <label for="date">日付:</label>
      <input type="date" id="date" v-model="date" required>
    </div>
    <div>
      <label for="ActualTime">活動時間:</label>
      <select v-model="ActualTime">
        <option v-for="option in timeOptions" :key="option" :value="option">
        {{ option }}
        </option>
      </select>
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

export default {
  created() {
        // 0.0 ~ 10まで、0.5単位で生成
        this.timeOptions = generateTimeOptions(0.0, 12, 0.5);
    },

  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref("")
    const message = ref("")
    const url = ref("")
    const ActualTime = ref("")
    const router = useRouter()

    const RegisterActual = async() =>{
        try {
          // 日付から年月日を取得
          const dateParts = date.value.split('-');
          year.value = dateParts[0];
          month.value = dateParts[1];
          day.value = dateParts[2];
          // 月と日が一桁の場合、表記を変更 例)09→9
          month.value = parseInt(month.value, 10);
          day.value = parseInt(day.value, 10);
          url.value = 'http://localhost:8000/activities/' + year.value + '/' + month.value + '/' + day.value + '/actual';
          const response = await axios.put(url.value, {
                                            actual_time: Number(ActualTime.value)
                                          })
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
              message.value = error.response.data.error;
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
      ActualTime,
      url,
      RegisterActual
    }
  }
}
</script>