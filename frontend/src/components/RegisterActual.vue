<template>
  <h3>活動時間の登録</h3>
  <form @submit.prevent="RegisterTarget">
      <div>
        <label for="year">年:</label>
        <input type="text" id="year" v-model="year" required>
      </div>
      <div>
        <label for="month">月:</label>
        <input type="text" id="month" v-model="month" required>
      </div>
      <div>
        <label for="day">日:</label>
        <input type="text" id="day" v-model="day" required>
      </div>
      <div>
        <label for="ActualTime">活動時間:</label>
        <input type="text" id="ActualTime" v-model="ActualTime" required>
      </div>
      <button type="submit">登録</button>
  </form>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div></div>
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
    const message = ref("")
    const url = ref("")
    const ActualTime = ref("")
    const router = useRouter()

    const RegisterTarget = async() =>{
        try {
          url.value = 'http://localhost:8000/activities/' + year.value + '/' + month.value + '/' + day.value + '/actual';
          const response = await axios.put(url.value, {
                                            actual_time: Number(ActualTime.value)
                                          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
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
      message,
      ActualTime,
      url,
      RegisterTarget
    }
  }
}
</script>