<template>
  <div class="container">
    <h2 class="mt-2 mb-4">{{ year }}年{{ month }}月{{ date }}日の活動実績</h2>
    <div class="row" v-if="activity_res">
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">目標時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activity_res.data.target_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">活動時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activity_res.data.actual_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ステータス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="statusClass[activity_res.data.status]" class="h3 fw-bold text-center">{{ STATUS_DICT[activity_res.data.status] }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="activity_msg" class="col-8" :class="activityAlertClass(activity_res)">
          {{ activity_msg }}
      </p>
    </div>
  </div>
  <div class="container">
    <h2>今月の給料</h2>
    <div class="row justify-content-center mb-4" v-if="income_res">
      <div class="col-8 mb-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="resultClass(income_res)" class="h3 fw-bold text-center">{{ income_res.data.total_income }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">月収</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ income_res.data.month_info.salary }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス-ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="resultClass(income_res)" class="h3 fw-bold text-center">{{ income_res.data.pay_adjustment }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center text-success">{{ income_res.data.month_info.total_bonus }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center text-danger">{{ income_res.data.month_info.total_penalty }}</span>
            万円
          </div>
        </div>
      </div>
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="income_msg" class="col-8 alert alert-warning p-3">
          {{ income_msg }}
      </p>
    </div>
  </div>
  <div class="container">
    <h2>Todo一覧</h2>
    <template v-if="todos.length">
      <table class="table table-striped table-responsive">
        <thead class="table-dark">
          <tr>
            <th style="width: 5%;">No.</th>
            <th>内容</th>
            <th>期限</th>
            <th style="width: 8%;"></th>
            <th style="width: 8%;"></th>
            <th style="width: 8%;"></th>
          </tr>
        </thead>
        <tbody v-for="(todo, index) in todos" :key="index">
          <tr>
            <td class="text-center align-middle">{{ index + 1 }}</td>
            <td class="text-center align-middle">{{ todo.action }}</td>
            <td class="text-center align-middle">{{ todo.due }}</td>
            <td><input class="btn btn-outline-primary btn-sm" type="button" value="編集" @click="editTodo(todo)"></td>
            <td><input class="btn btn-outline-success btn-sm" type="button" value="終了" @click="finishTodo(todo.todo_id)"></td>
            <td><input class="btn btn-outline-danger btn-sm" type="button" value="削除" @click="deleteTodo(todo.todo_id)"></td>
          </tr>
        </tbody>
      </table>
    </template>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="todo_msg" class="col-8 bg-white rounded shadow p-3">
          {{ todo_msg }}
      </p>
    </div>
  </div>
</template>


<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { useTodoStore } from '@/store/todo';
import { STATUS_DICT, resultClass, statusClass, activityAlertClass } from './lib';

export default {
  setup() {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth() + 1;
    const date = today.getDate();
    const activity_msg = ref("")
    const activity_res = ref()
    const income_msg = ref("")
    const income_res = ref()
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
          activity_res.value = await axios.get(act_url,
                                              {headers: {Authorization: authStore.getAuthHeader}})
          if (activity_res.value.status===200){
            const bonusInYen = parseInt(activity_res.value.data.bonus * 10000, 10)
            const penaltyInYen = parseInt(activity_res.value.data.penalty * 10000, 10)
            if (activity_res.value.data.status === "success"){
              activity_msg.value += `目標達成!|\nボーナス:${activity_res.value.data.bonus}万円(${bonusInYen}円)`
            } else if(activity_res.value.data.status === "failure"){
              activity_msg.value += `目標失敗...\nペナルティ:${activity_res.value.data.penalty}万円(${penaltyInYen}円)`
            } else {
              if (activity_res.value.data.target_time <= activity_res.value.data.actual_time) {
              activity_msg.value += `目標達成!活動を終了してください\n確定後のボーナス:${activity_res.value.data.bonus}万円(${bonusInYen}円)`
              } else {
              activity_msg.value += `このままだと、${activity_res.value.data.penalty}万円(${penaltyInYen}円)のペナルティが発生`}
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
          income_res.value = await axios.get(income_url,
                                          {headers: {Authorization: authStore.getAuthHeader}}
          )
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
      activity_res,
      income_msg,
      income_res,
      todos,
      todo_msg,
      year,
      month,
      date,
      updateTodos,
      deleteTodo,
      finishTodo,
      editTodo,
      STATUS_DICT,
      resultClass,
      statusClass,
      activityAlertClass
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