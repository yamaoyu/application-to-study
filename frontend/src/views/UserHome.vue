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
  <div>
    <router-link to="/register/salary">月収登録</router-link>
  </div>
  <div>
    <router-link to="/register/target">目標時間登録</router-link>
  </div>
  <div>
    <router-link to="/register/actual">活動時間登録</router-link>
  </div>
  <div>
    <router-link to="/finish/activity">活動を終了</router-link>
  </div>
  <div>
    <router-link to="/view/month-activities">月ごとの活動記録</router-link>
  </div>
  <div>
    <router-link to="/view/all-activities">全期間の活動記録</router-link>
  </div>
  <div>
    <router-link to="/register/todo">Todoを登録</router-link>
  </div>
  <div>
    <router-link to="/register/inquiry">問い合わせ</router-link>
  </div>
</template>


<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

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
    const store = useStore()


    const deleteTodo = async(todoId) =>{
      try {
          const delete_url = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoId
          const response = await axios.delete(
            delete_url, 
            { 
              headers: {
              Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}
            }
          )
        if (response.status===204){
            // 削除に成功したらtodoを更新する
            const todo_url = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
            const todo_res = await axios.get(todo_url,
                                          {headers: {Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}})
            todos.value = todo_res.data;
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
              Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}
            }
          )
        if (response.status===200){
            // ステータスを終了にしたらtodoを更新する
            const todo_url = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
            const todo_res = await axios.get(todo_url,
                                          {headers: {Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}})
            todos.value = todo_res.data;
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
      store.commit('moduleTodo/editTodoInfo', JSON.stringify(todoInfo))
      router.push({"name":"EditTodo"}
      )
    }

    onMounted( async() =>{
        // その日の活動実績を取得
        try {
          const act_url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + date;
          const activity_res = await axios.get(act_url,
                                              {headers: {Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}})
          if (activity_res.status===200){
            activity_msg.value = [activity_res.data.date,
                                  `\n目標時間:${activity_res.data.target_time}時間`,
                                  `\n活動時間:${activity_res.data.actual_time}時間`,
                                  `\nステータス:${activity_res.data.is_achieved}`,
                                  `\nボーナス:${(activity_res.data.bonus * 10)}千円`
            ].join('');
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
                                          {headers: {Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}}
          )
          if (earn_res.status===200){
            income_msg.value = [`今月の月収:${earn_res.data["今月の詳細"].salary}万円`,
                                `\n合計ボーナス:${(earn_res.data["今月の詳細"].bonus * 10000)}円`,
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
                                          {headers: {Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}})
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