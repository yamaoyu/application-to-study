<template>
  <div class="container">
    <h2 class="mt-2 mb-4">{{ year }}年{{ month }}月{{ date }}日の活動実績</h2>
    <div class="row" v-if="activityRes">
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">目標時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activityRes.data.target_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">活動時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activityRes.data.actual_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ステータス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getStatusColors[activityRes.data.status]" class="h3 fw-bold text-center">{{ STATUS_DICT[activityRes.data.status] }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="activityMsg" class="col-8" :class="getActivityAlert(activityStatus)">
          {{ activityMsg }}
      </p>
    </div>
  </div>
  <div class="container">
    <h2>今月の給料</h2>
    <div class="row justify-content-center mb-4" v-if="incomeRes">
      <div class="col-8 mb-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(incomeRes)" class="h3 fw-bold text-center">{{ incomeRes.data.total_income }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">月収</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ incomeRes.data.month_info.salary }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス-ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(incomeRes)" class="h3 fw-bold text-center">{{ incomeRes.data.pay_adjustment }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center text-success">{{ incomeRes.data.month_info.total_bonus }}</span>
            万円
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center text-danger">{{ incomeRes.data.month_info.total_penalty }}</span>
            万円
          </div>
        </div>
      </div>
    </div>
    <div class="row d-flex align-items-center justify-content-center my-3">
      <p v-if="incomeMsg" class="col-8 alert alert-warning p-3">
          {{ incomeMsg }}
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
      <p v-if="todoMsg" class="col-8 alert alert-warning p-3">
          {{ todoMsg }}
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
import { jwtDecode } from 'jwt-decode';
import { STATUS_DICT, getAdjustmentColors, getStatusColors, getActivityAlert, commonError, verifyRefreshToken } from './lib';

export default {
  setup() {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth() + 1;
    const date = today.getDate();
    const activityMsg = ref("")
    const activityRes = ref()
    const activityStatus = ref("")
    const incomeMsg = ref("")
    const incomeRes = ref()
    const todos = ref([])
    const todoMsg = ref("")
    const router = useRouter()
    const authStore = useAuthStore()
    const todoStore = useTodoStore()
    const { handleError: todoError } = commonError(todoMsg, router)

    const updateTodos = async() =>{
      // todo更新後、データを更新する
      try {
        const todoUrl = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
        const todoRes = await axios.get(todoUrl,
                                      {headers: {Authorization: authStore.getAuthHeader}})
        todos.value = todoRes.data;
      } catch (todo_err){
        switch (todo_err.response.status){
          case 404:
          case 500:
            todos.value = []
            todoMsg.value = todo_err.response.data.detail;
            break
          default:
            todoMsg.value = "todoの取得に失敗しました"
        }
      }
    }

    const deleteTodoRequest = async(todoId) =>{
      const deleteUrl = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoId
      const response = await axios.delete(
        deleteUrl, 
        { 
          headers: {
          Authorization: authStore.getAuthHeader}
        }
      )

      return response
    }

    const deleteTodo = async(todoId) =>{
      try {
          const response = await deleteTodoRequest(todoId)
        if (response.status===204){
            await updateTodos();
          }
      } catch (error) {
        if (error.response?.status === 401) {
          try {
            // リフレッシュトークンを検証して新しいアクセストークンを取得
            const tokenResponse = await verifyRefreshToken();
            // 新しいアクセストークンをストアに保存
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await deleteTodoRequest(todoId);
            await updateTodos();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          todoError(error)
        }
        }
    }

    const finishTodoRequest = async(todoId) =>{
      const finish_url = process.env.VUE_APP_BACKEND_URL + 'todos/finish/' + todoId
      const response = await axios.put(
        finish_url, 
        {},
        { 
          headers: {
          Authorization: authStore.getAuthHeader}
        }
      )
      return response
    }

    const finishTodo = async(todoId) =>{
      try {
        const response = await finishTodoRequest(todoId)
        if (response.status===200){
            await updateTodos();
          }
      } catch (error) {
        if (error.response?.status === 401) {
          try {
            // リフレッシュトークンを検証して新しいアクセストークンを取得
            const tokenResponse = await verifyRefreshToken();
            // 新しいアクセストークンをストアに保存
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await finishTodoRequest(todoId);
            await updateTodos();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          todoError(error)
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
          activityRes.value = await axios.get(act_url,
                                              {headers: {Authorization: authStore.getAuthHeader}})
          if (activityRes.value.status===200){
            activityStatus.value = activityRes.value.data.status
            const bonusInYen = parseInt(activityRes.value.data.bonus * 10000, 10)
            const penaltyInYen = parseInt(activityRes.value.data.penalty * 10000, 10)
            if (activityRes.value.data.status === "success"){
              activityMsg.value = `目標達成!|\nボーナス:${activityRes.value.data.bonus}万円(${bonusInYen}円)`
            } else if(activityRes.value.data.status === "failure"){
              activityMsg.value = `目標失敗...\nペナルティ:${activityRes.value.data.penalty}万円(${penaltyInYen}円)`
            } else {
              if (activityRes.value.data.target_time <= activityRes.value.data.actual_time) {
              activityMsg.value = `目標達成!活動を終了してください\n確定後のボーナス:${activityRes.value.data.bonus}万円(${bonusInYen}円)`
              } else {
              activityMsg.value = `このままだと、${activityRes.value.data.penalty}万円(${penaltyInYen}円)のペナルティが発生`}
            }
          }
        } catch (act_err) {
          activityStatus.value = ""
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
                activityMsg.value = act_err.response.data.detail;
                break;
              default:
                activityMsg.value = "情報の取得に失敗しました";}
          } else if (act_err.request){
            activityMsg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            activityMsg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }

        // その月の月収を取得
        try{
          const income_url = process.env.VUE_APP_BACKEND_URL + 'incomes/' + year + '/' + month;
          incomeRes.value = await axios.get(income_url,
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
                incomeMsg.value = income_err.response.data.detail;
                break;
              default:
                incomeMsg.value = "情報の取得に失敗しました";}
          } else if (income_err.request){
            incomeMsg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            incomeMsg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }

        // そのユーザーの未完了のtodoを取得
        try{
          const todoUrl = process.env.VUE_APP_BACKEND_URL + 'todos/?status=False'
          const todoRes = await axios.get(todoUrl,
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (todoRes.status==200){
            todos.value = todoRes.data;
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
                todoMsg.value = todo_err.response.data.detail;
                break;
              default:
                todoMsg.value = "情報の取得に失敗しました";}
          } else if (todo_err.request){
            todoMsg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            todoMsg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }
    )

    return {
      activityMsg,
      activityRes,
      activityStatus,
      incomeMsg,
      incomeRes,
      todos,
      todoMsg,
      year,
      month,
      date,
      updateTodos,
      deleteTodo,
      finishTodo,
      editTodo,
      STATUS_DICT,
      getAdjustmentColors,
      getStatusColors,
      getActivityAlert
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