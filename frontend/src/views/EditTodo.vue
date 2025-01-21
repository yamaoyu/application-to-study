<template>
  <h3>Todoの編集</h3>
  <form @submit.prevent="editTodo">
      <div>
        <label for="action">Todo:</label>
        <textarea name="action" id="action" for="action" v-model="action" required></textarea>
      </div>
      <div>
        <label for="due">期限:</label>
        <input type="date" id="date" v-model="due" required>
        <input type="button" value="今日" @click="insertToday">
        <input type="button" value="-1" @click="decreaseOneDay">
        <input type="button" value="+1" @click="increaseOneDay">
      </div>
      <button type="submit">更新</button>
  </form>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { useTodoStore } from '@/store/todo';
import { getToday, getNextDay, getPreviousDay } from './lib/dateUtils';

export default {
  setup() {
    const message = ref("")
    const action = ref("")
    const due = ref()
    const router = useRouter()
    const authStore = useAuthStore()
    const todoStore = useTodoStore()

    const insertToday = async() =>{
      due.value = getToday();
    }

    const decreaseOneDay = async() => {
      if (due.value) {
        due.value = getPreviousDay(due.value);
        message.value = "";
      } else {
        message.value = "日付が指定されていません";
      }
    }

    const increaseOneDay = async() => {
      if (due.value !== '') {
        due.value = getNextDay(due.value);
        message.value = "";
      } else{
        message.value = "日付が指定されていません";
      }
    }

    const editTodo = async() =>{
      try{
          const url = process.env.VUE_APP_BACKEND_URL + 'todos/' + todoStore.todoId
          const response = await axios.put(url,
                                          {action: action.value, due:due.value},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (response.status===200){
            message.value = [
              response.data.message,
              `\n更新後のTodo:${response.data.action}`,
              `\n更新後の期限:${response.data.due}`
            ].join('');
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
      todoStore,
      insertToday,
      increaseOneDay,
      decreaseOneDay,
      editTodo
    }
  }
}
</script>