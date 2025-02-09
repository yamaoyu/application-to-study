<template>
  <div style="white-space: pre-wrap;">
    <h3>今日の活動実績</h3>
    <p v-if="activity_msg" class="activity_msg">{{ activity_msg }}</p>
  </div>
  <div style="white-space: pre-wrap;">
    <h3>今月の給料</h3>
    <p v-if="income_msg" class="income_msg">{{ income_msg }}</p>
  </div>
  <div>
    <h3>Todo一覧</h3>
    <template v-if="todos.length">
      <ul>
        <li v-for="(todo, index) in todos" :key="index" class="todo-item">
          {{ index + 1 }}: {{ todo.action }} (期限: {{ todo.due }})
          <input type="button" value="編集" @click="editTodo(todo)">
          <input type="button" value="終了" @click="finishTodo(todo.todo_id)">
          <input type="button" value="削除" @click="deleteTodo(todo.todo_id)">
        </li>
      </ul>
    </template>
    <p v-else>{{ todo_msg }}</p>
  </div>
  <br>
</template>


<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { useTodoStore } from '@/store/todo';
import { STATUS_DICT } from './lib';

export default {
  setup() {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth() + 1;
    const date = today.getDate();
    const activity_msg = ref("")
    const income_msg = ref("")
    const todos = ref([])
    const todo_msg = ref("")
    const router = useRouter()
    const authStore = useAuthStore()
    const todoStore = useTodoStore()

    const updateTodos = async() =>{
      // todo更新後、データを更新する
      try {
        const todo_url = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
        const todo_res = await axios.get(todo_url,
                                      {headers: {Authorization: authStore.getAuthHeader}})
        todos.value = todo_res.data;
      } catch (todo_err){
        switch (todo_err.response.status){
          case 404:
          case 500:
            todos.value = []
            todo_msg.value = todo_err.response.data.detail;
            break
          default:
            todo_msg.value = "todoの取得に失敗しました"
        }
      }
    }


    const deleteTodo = async(todoId) =>{
      try {
          const delete_url = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoId
          const response = await axios.delete(
            delete_url, 
            { 
              headers: {
              Authorization: authStore.getAuthHeader}
            }
          )
        if (response.status===204){
            await updateTodos();
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
              case 500:
                todo_msg.value =  "todoの削除に失敗しました"
                break;
              default:
                todo_msg.value = error.response.data.detail;}
          } else if (error.request){
            todo_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            todo_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
    }

    const finishTodo = async(todoId) =>{
      try {
          const finish_url = process.env.VUE_APP_BACKEND_URL + 'todos/finish/' + todoId
          const response = await axios.put(
            finish_url, 
            {},
            { 
              headers: {
              Authorization: authStore.getAuthHeader}
            }
          )
        if (response.status===200){
            await updateTodos();
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
              case 500:
                todo_msg.value =  "todoの削除に失敗しました"
                break;
              default:
                todo_msg.value = error.response.data.detail;}
          } else if (error.request){
            todo_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            todo_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
    }

    const editTodo = async(todoInfo) =>{
      todoStore.saveTodo(todoInfo["todo_id"], todoInfo["action"], todoInfo["due"])
      router.push({"name":"EditTodo"}
      )
    }


    onMounted( async() =>{
        // その日の活動実績を取得
        try {
          const act_url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + date;
          const activity_res = await axios.get(act_url,
                                              {headers: {Authorization: authStore.getAuthHeader}})
          if (activity_res.status===200){
            const activity = activity_res.data
            activity_msg.value = [activity.date,
                                  `\n目標時間:${activity.target_time}時間`,
                                  `\n活動時間:${activity.actual_time}時間`,
                                  `\nステータス:${STATUS_DICT[activity.status]}`
            ].join('');
            const bonusInYen = parseInt(activity.bonus * 10000, 10)
            const penaltyInYen = parseInt(activity.penalty * 10000, 10)
            if (activity.status === "success"){
              activity_msg.value += `\nボーナス:${activity.bonus}万円(${bonusInYen}円)`
            } else if(activity.status === "failure"){
              activity_msg.value += `\nペナルティ:${activity.penalty}万円(${penaltyInYen}円)`
            } else {
              if (activity.target_time <= activity.actual_time) {
              activity_msg.value += `\n目標達成!活動を終了してください\n確定後のボーナス:${activity.bonus}万円(${bonusInYen}円)`
              } else {
              activity_msg.value += `\nこのままだと、${activity.penalty}万円(${penaltyInYen}円)のペナルティが発生`}
            }
          }
        } catch (act_err) {
          if (act_err.response){
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
                activity_msg.value = "情報の取得に失敗しました";}
          } else if (act_err.request){
            activity_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            activity_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }

        // その月の月収を取得
        try{
          const income_url = process.env.VUE_APP_BACKEND_URL + 'incomes/' + year + '/' + month;
          const earn_res = await axios.get(income_url,
                                          {headers: {Authorization: authStore.getAuthHeader}}
          )
          if (earn_res.status===200){
            income_msg.value = [`月収:${earn_res.data["今月の詳細"].salary}万円`,
                                `\nボーナス:${(earn_res.data["今月の詳細"].total_bonus)}万円`,
                                `\nペナルティ:${(earn_res.data["今月の詳細"].total_penalty)}万円`,
                                `\nボーナス換算後の月収:${earn_res.data["ボーナス換算後の月収"]}万円`
          ].join('');
          }
        } catch (income_err) {
          if (income_err.response){
            switch (income_err.response.status){
              case 401:
                router.push(
                  {"path":"/login",
                    "query":{message:"再度ログインしてください"}
                  })
                break;
              case 404:
              case 500:
                income_msg.value = income_err.response.data.detail;
                break;
              default:
                income_msg.value = "情報の取得に失敗しました";}
          } else if (income_err.request){
            income_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            income_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }

        // そのユーザーの未完了のtodoを取得
        try{
          const todo_url = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
          const todo_res = await axios.get(todo_url,
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (todo_res.status==200){
            todos.value = todo_res.data;
          }
        } catch (todo_err) {
          if (todo_err.response){
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
                todo_msg.value = "情報の取得に失敗しました";}
          } else if (todo_err.request){
            todo_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            todo_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }
    )

    return {
      activity_msg,
      income_msg,
      todos,
      todo_msg,
      year,
      month,
      date,
      updateTodos,
      deleteTodo,
      finishTodo,
      editTodo
    }
  }
}
</script>

<style>
li{
  list-style: none;
}
.todo-item {
  margin: 0; /* 要素間の余白を削除 */
  padding: 0;
  line-height: 1.5; /* 行の高さを調整 */
}
</style>