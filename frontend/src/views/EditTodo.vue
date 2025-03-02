<template>
  <h3>Todoの編集</h3>
  <form @submit.prevent="editTodo">
    <div class="container col-10 d-flex justify-content-center">
      <span class="input-group-text">内容</span>
      <div class="input-group">
        <textarea
          v-model="action"
          class="form-control"
          placeholder="Todoの内容"
          maxlength="256"
          >
        </textarea>
      </div>
    </div>
    <div class="container col-10 d-flex justify-content-center mt-3">
      <div class="input-group">
        <span class="input-group-text">期限</span>
        <input
          type="date"
          v-model="due"
          class="form-control col-2"
          min="2024-01-01"
        />
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseDay(-1)"
          >
          前日
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="increaseDay(1)"
          >
          翌日
        </button>
      </div>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3">更新</button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 col-8" :class="getResponseAlert(statusCode)">{{ message }}</p>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { useTodoStore } from '@/store/todo';
import { changeDate, getResponseAlert } from './lib/index';

export default {
  setup() {
    const message = ref("")
    const action = ref("")
    const due = ref()
    const router = useRouter()
    const statusCode = ref()
    const authStore = useAuthStore()
    const todoStore = useTodoStore()

    const { increaseDay } = changeDate(due, message);

    const editTodo = async() =>{
      try{
          const url = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoStore.todoId
          const response = await axios.put(url,
                                          {action: action.value, due:due.value},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          statusCode.value = response.status
          if (response.status===200){
            message.value = [
              response.data.message,
              `\n更新後のTodo:${response.data.action}`,
              `\n更新後の期限:${response.data.due}`
            ].join('');
          }
        } catch (error) {
          statusCode.value = null;
          if (error.response){
            switch (error.response.status){
              case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
                break;
              case 404:
              case 500:
                message.value = error.response.data.detail;
                break;
              default:
                message.value = "todoの更新に失敗しました";}
          } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }

    onMounted( async() =>{
        action.value = todoStore.action
        due.value = todoStore.due
    }

    )

    return {
      message,
      action,
      due,
      statusCode,
      todoStore,
      increaseDay,
      getResponseAlert,
      editTodo
    }
  }
}
</script>