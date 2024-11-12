<template>
  <h3>活動時間の登録</h3>
  <form @submit.prevent="RegisterTarget">
    <div>
      <label for="date">日付:</label>
      <input type="date" id="date" v-model="date" required>
    </div>
    <div>
      <label for="ActualTime">活動時間:</label>
      <select id="ActualTime" v-model="ActualTime" required>
        <option value="">-</option>
        <option value="0">0</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5">5</option>
        <option value="6">6</option>
        <option value="7">7</option>
        <option value="8">8</option>
        <option value="9">9</option>
        <option value="10">10</option>
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

export default {
  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref("")
    const message = ref("")
    const url = ref("")
    const ActualTime = ref("")
    const router = useRouter()

    const RegisterTarget = async() =>{
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
      ActualTime,
      url,
      RegisterTarget
    }
  }
}
</script>