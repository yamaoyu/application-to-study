<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="registerTodo">
      <div>
        <label for="action">Todo:</label>
        <input type="text" id="action" v-model="action" required>
      </div>
      <div>
        <label for="due">期限:</label>
        <input type="date" id="date" v-model="due" required>
        <input type="button" value="今日" @click="insertToday">
        <input type="button" value="-1" @click="decreaseOneDay">
        <input type="button" value="+1" @click="increaseOneDay">
      </div>
      <button type="submit">登録</button>
  </form>
  <div style="white-space: pre-wrap;">
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { changeDate } from './lib/index';

export default {
  setup() {
    const message = ref("")
    const action = ref("")
    const due = ref("")
    const router = useRouter()
    const authStore = useAuthStore()
    const { insertToday, decreaseOneDay, increaseOneDay } = changeDate(due, message);

    const registerTodo = async() =>{
        try {
          const url = process.env.VUE_APP_BACKEND_URL + 'todos'
          const response = await axios.post(
            url, 
            {
              action: action.value,
              due: due.value
            },
            { 
              headers: {
              Authorization:  authStore.getAuthHeader}
            }
          )
          if (response.status===201){
            message.value = [response.data.message + "\n",
                            "内容:" + response.data.action + "\n",
                            "期限:" + response.data.due].join("")
            // フィールドをクリア
            action.value = ""
            due.value = ""
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
              case 422:
                message.value = error.response.data.detail;
                break;
              case 500:
                message.value =  "todoの登録に失敗しました"
                break;
              default:
                message.value = error.response.data.detail;}
          } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }

    return {
      message,
      action,
      due,
      insertToday,
      increaseOneDay,
      decreaseOneDay,
      registerTodo
    }
  }
}
</script>