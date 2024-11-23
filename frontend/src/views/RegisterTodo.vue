<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="RegisterTodo">
      <div>
        <label for="action">Todo:</label>
        <input type="text" id="action" v-model="action" required>
      </div>
      <div>
        <label for="due">期限:</label>
        <input type="date" id="date" v-model="due" required>
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

export default {
  setup() {
    const message = ref("")
    const action = ref("")
    const due = ref("")
    const router = useRouter()

    const RegisterTodo = async() =>{
        try {
          const response = await axios.post('http://localhost:8000/todos', {
                                            action: action.value,
                                            due: due.value
                                          })
          if (response.status===201){
            message.value = [response.data.message + "\n",
                            "内容:" + response.data.action + "\n",
                            "期限:" + response.data.due].join("")
          }
        } catch (error) {
          switch (error.response.status){
            case 401:
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
              break;
            case 422:
              message.value = error.response.data.error;
              break;
            case 500:
              message.value =  "todoの登録に失敗しました"
              break;
            default:
              message.value = error.response.data.detail;
          }
        }
      }

    return {
      message,
      action,
      due,
      RegisterTodo
    }
  }
}
</script>