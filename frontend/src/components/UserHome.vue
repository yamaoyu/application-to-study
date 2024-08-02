<template>
  <h3>今月の活動実績</h3>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
    <p v-if="date" class="date">{{ date }}</p>
  </div>
  <router-link to="/form/income">月収登録</router-link>
</template>

<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const today = new Date();
    const year = ("00" + today.getFullYear()).slice(-4);
    const month = ("00" + (today.getMonth() + 1)).slice(-2);
    const date = year + "-" + month;
    const message = ref("")
    const router = useRouter()

    onMounted( async() =>{
        try {
          const response = await axios.get('http://localhost:8000/month${date}', {
            data:{date: date.value}
          },)
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
            message.value = error.response.data.detail;
          }else{
            message.value = "情報の取得に失敗しました";
          }
        }
      })

    return {
      message,
      date
    }
  }
}
</script>