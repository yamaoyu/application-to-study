<template>
  <h3>今日の活動実績</h3>
  <div>
    <p v-if="activity_msg" class="activity_msg">{{ activity_msg }}</p>
  </div>
  <div>
    <p v-if="salary_msg" class="salary_msg">{{ salary_msg }}</p>
  </div>
  <div>
    <p v-if="todo_message" class="todo_message">{{ todo_message }}</p>
  </div>
  <div>
    <router-link to="/form/income">月収登録</router-link>
  </div>
  <div>
    <router-link to="/form/target">目標時間登録</router-link>
  </div>
  <div>
    <router-link to="/form/actual">活動時間登録</router-link>
  </div>
  <div>
    <router-link to="/finish/activity">活動を終了</router-link>
  </div>
  <div>
    <router-link to="/month">月ごとの活動記録</router-link>
  </div>
  <div>
    <router-link to="/form/todo">Todoを登録</router-link>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth() + 1;
    const date = today.getDate();
    const activity_msg = ref("")
    const salary_msg = ref("")
    const todo_message = ref("")
    const url = ref("")
    const router = useRouter()

    onMounted( async() =>{
        // その日の活動実績を取得
        try {
          url.value = 'http://localhost:8000/activities/' + year + '/' + month + '/' + date;
          const response = await axios.get(url.value)
          if (response.status===200){
            activity_msg.value = response.data
          }
        } catch (error) {
          if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if(error.response.data.detail===404){
            activity_msg.value = error.response.data.detail;
          }else if (error.response.status!==500){
            activity_msg.value = error.response.data.detail;
          }else{
            activity_msg.value = "情報の取得に失敗しました";
          }
        }

        // その月の月収を取得
        try{
          url.value = 'http://localhost:8000/income/' + year + '/' + month;
          const response = await axios.get(url.value)
          if (response.status===200){
            salary_msg.value = response.data
          }
        } catch (error) {
          if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if(error.response.data.detail===404){
            salary_msg.value = error.response.data.detail;
          }else if (error.response.status!==500){
            salary_msg.value = error.response.data.detail;
          }else{
            salary_msg.value = "情報の取得に失敗しました";
          }
        }

        // そのユーザーのtodoを取得
        try{
          url.value = 'http://localhost:8000/todo/'
          const response = await axios.get(url.value)
          if (response.status===200){
            todo_message.value = response.data
          }
        } catch (error) {
          if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if(error.response.data.detail===404){
            todo_message.value = error.response.data.detail;
          }else if (error.response.status!==500){
            todo_message.value = error.response.data.detail;
          }else{
            todo_message.value = "情報の取得に失敗しました";
          }
        }

      })

    return {
      activity_msg,
      salary_msg,
      todo_message,
      year,
      month,
      date
    }
  }
}
</script>