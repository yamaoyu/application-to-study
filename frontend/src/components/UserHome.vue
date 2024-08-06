<template>
  <h3>今月の活動実績</h3>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
    <p v-if="year" class="year">{{ year }}</p>
    <p v-if="month" class="month">{{ month }}</p>
  </div>
  <router-link to="/form/income">月収登録</router-link>
  <router-link to="/form/target">目標時間登録</router-link>
</template>

<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;
    const message = ref("")
    const url = ref("")
    const router = useRouter()

    onMounted( async() =>{
        try {
          url.value = 'http://localhost:8000/activities/' + year + '/' + month;
          const response = await axios.get(url.value)
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===200){
            message.value = response.data
          }
        } catch (error) {
          // エラー処理（ユーザーへの通知など）
          if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if (error.response.status!==500){
            message.value = error.response.data.detail;
          }else{
            message.value = "情報の取得に失敗しました";
          }
        }
      })

    return {
      message,
      year,
      month
    }
  }
}
</script>