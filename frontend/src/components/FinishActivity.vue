<template>
  <h3>活動を終了</h3>
  <form @submit.prevent="FinishActivity">
    <div>
      <label for="date">日付:</label>
      <input type="date" id="date" v-model="date" required>
    </div>
    <button type="submit">終了</button>
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

export default {
  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref("")
    const message = ref("")
    const url = ref("")
    const router = useRouter()

    const FinishActivity = async() =>{
        try {
          // 日付から年月日を取得
          year.value = date.value.split('-')[0];
          month.value = date.value.split('-')[1];
          day.value = date.value.split('-')[2];
          // 月と日が一桁の場合、表記を変更 例)09→9
          month.value = parseInt(month.value, 10);
          day.value = parseInt(day.value, 10);
          url.value = 'http://localhost:8000/activities/' + year.value + '/' + month.value + '/' + day.value + '/finish';
          const response = await axios.put(url.value)
          if (response.status===200){
            message.value = response.data.message
          }
        } catch (error) {
          // エラー処理（ユーザーへの通知など）
          if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if (error.response.status!==500){
            message.value = error.response.data.detail
          }else{
            message.value = "活動時間の登録に失敗しました";
          }
        }
      }

    return {
      year,
      month,
      day,
      date,
      message,
      url,
      FinishActivity
    }
  }
}
</script>