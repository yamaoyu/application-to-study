<template>
  <h3>目標時間の登録</h3>
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
        <label for="TargetTime">目標時間:</label>
        <input type="text" id="TargetTime" v-model="TargetTime" required>
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
    const TargetTime = ref("")
    const router = useRouter()

    const RegisterTarget = async() =>{
        try {
          url.value = 'http://localhost:8000/activities/' + year.value + '/' + month.value + '/' + day.value + '/target';
          const response = await axios.post(url.value, {
                                            target_time: Number(TargetTime.value)
                                          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===201){
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
            message.value = "目標時間の登録に失敗しました";
          }
        }
      }

    return {
      year,
      month,
      day,
      message,
      TargetTime,
      url,
      RegisterTarget
    }
  }
}
</script>