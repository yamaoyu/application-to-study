<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="RegisterTodo">
      <div>
        <label for="action">Todo:</label>
        <input type="text" id="action" v-model="action" required>
      </div>
      <button type="submit">登録</button>
  </form>
  <div>
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

export default {
  setup() {
    const message = ref("")
    const action = ref("")
    const router = useRouter()

    const RegisterTodo = async() =>{
        try {
          const response = await axios.post('http://localhost:8000/todo', {
                                            action: action.value
                                          })
          if (response.status===201){
            message.value = response.data
          }
        } catch (error) {
          // エラー処理（ユーザーへの通知など）
          if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if (error.response.status!==500){
            message.value = error.response.data.detail
          }else{
            message.value = "活動時間の登録に失敗しました";
          }
        }
      }

    return {
      message,
      action,
      RegisterTodo
    }
  }
}
</script>