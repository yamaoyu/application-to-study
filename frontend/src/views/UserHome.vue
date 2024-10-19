<template>
  <div style="white-space: pre-wrap;">
    <h3>今日の活動実績</h3>
    <p v-if="activity_msg" class="activity_msg">{{ activity_msg }}</p>
  </div>
  <div style="white-space: pre-wrap;">
    <h3>今月の給料</h3>
    <p v-if="salary_msg" class="salary_msg">{{ salary_msg }}</p>
  </div>
  <div>
    <h3>Todo一覧</h3>
    <template v-if="todos.length">
      <ul v-for="(todo, index) in todos" :key="index" class="todo-item">
        <li v-if="todo.action" class="todos">{{ index + 1 }}: {{ todo.action }}</li>
      </ul>
    </template>
    <p v-else>{{ todo_msg }}</p>
  </div>
  <br>
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
    const todos = ref("")
    const todo_msg = ref("")
    const url = ref("")
    const router = useRouter()

    onMounted( async() =>{
        // その日の活動実績を取得
        try {
          url.value = 'http://localhost:8000/activities/' + year + '/' + month + '/' + date;
          const activity_res = await axios.get(url.value)
          if (activity_res.status===200){
            activity_msg.value = activity_res.data.date
            activity_msg.value += "\n目標時間:" + activity_res.data.target_time + "時間"
            activity_msg.value += "\n活動時間:" + activity_res.data.actual_time + "時間"
            activity_msg.value += "\nステータス:" + activity_res.data.is_achieved
            activity_msg.value += "\nボーナス:" + (activity_res.data.bonus * 10) + "千円"
          }
        } catch (act_err) {
          switch (act_err.response.status){
            case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
              break;
            case 404:
            case 500:
              activity_msg.value = act_err.response.data.detail;
              break;
            default:
              activity_msg.value = "情報の取得に失敗しました";
          }
        }

        // その月の月収を取得
        try{
          url.value = 'http://localhost:8000/earnings/' + year + '/' + month;
          const earn_res = await axios.get(url.value)
          if (earn_res.status===200){
            salary_msg.value = "今月の月収:" + earn_res.data["今月の詳細"].monthly_income + "万円"
            salary_msg.value += "\n合計ボーナス:" + (earn_res.data["今月の詳細"].bonus * 10000) + "円"
            salary_msg.value += "\nボーナス換算後の月収:" + earn_res.data["ボーナス換算後の月収"] + "万円"
          }
        } catch (earn_err) {
          switch (earn_err.response.status){
            case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
              break;
            case 404:
            case 500:
              salary_msg.value = earn_err.response.data.detail;
              break;
            default:
              salary_msg.value = "情報の取得に失敗しました";
          }
        }

        // そのユーザーのtodoを取得
        try{
          url.value = 'http://localhost:8000/todos/'
          const todo_res = await axios.get(url.value)
          if (todo_res.status===200){
            todos.value = todo_res.data;
          }
        } catch (todo_err) {
          todos.value = "";
          switch (todo_err.response.status){
            case 401:
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
              break;
            case 404:
            case 500:
              todo_msg.value = todo_err.response.data.detail;
              break;
            default:
              todo_msg.value = "情報の取得に失敗しました";
          }
        }
      }
    )

    return {
      activity_msg,
      salary_msg,
      todos,
      todo_msg,
      year,
      month,
      date
    }
  }
}
</script>