<template>
  <h3>今日の活動実績</h3>
  <div style="white-space: pre-wrap;">
    <p v-if="activity_msg" class="activity_msg">{{ activity_msg }}</p>
  </div>
  <div style="white-space: pre-wrap;">
    <p v-if="salary_msg" class="salary_msg">{{ salary_msg }}</p>
  </div>
  <ul v-for="(todo, index) in todo_message" :key="index" class="todo-item">
    <li v-if="todo" class="todo_message">{{ index + 1 }}: {{ todo.action }}</li>
  </ul>
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
  <div>
    <router-link to="/form/inquiry">問い合わせ</router-link>
  </div>
</template>

<style scoped>
.todo-item {
  margin: 0; /* 要素間の余白を削除 */
  padding: 0;
  line-height: 1.5; /* 行の高さを調整 */
}
</style>

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
            activity_msg.value = response.data.date
            activity_msg.value += "\n目標時間:" + response.data.target_time + "時間"
            activity_msg.value += "\n活動時間:" + response.data.actual_time + "時間"
            activity_msg.value += "\nステータス:" + response.data.is_achieved
            activity_msg.value += "\nボーナス:" + (response.data.bonus * 10) + "千円"
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
            salary_msg.value = "今月の月収:" + response.data["今月の詳細"].monthly_income + "万円"
            salary_msg.value += "\n合計ボーナス:" + (response.data["今月の詳細"].bonus * 10000) + "円"
            salary_msg.value += "\nボーナス換算後の月収:" + response.data["ボーナス換算後の月収"] + "万円"
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