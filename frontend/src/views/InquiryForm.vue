<template>
  <form @submit.prevent="SendInquiry">
    <div>
      <label for="category">カテゴリ:</label><br>
      <input type="radio" id="category-request" value="要望" v-model="category" required>要望
      <input type="radio" id="category-error" value="エラー報告" v-model="category" required>エラー報告
      <input type="radio" id="category-other" value="その他" v-model="category" required>その他
    </div>
    <div>
      <label for="detail">詳細(最大256文字):</label><br>
      <textarea id="detail" maxlength="256" v-model="detail" required></textarea>
    </div>
    <button type="submit">送信</button>
  </form>
  <p v-if="message" class="message">{{ message }}</p>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>
  
  <script>
  import { ref } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router';
  
  export default {
    setup() {
      const category = ref('')
      const detail = ref('')
      const message = ref('')
      const router = useRouter()
  
      const SendInquiry = async() => {
        try {
          const response = await axios.post('http://localhost:8000/inquiries', {
            category: category.value,
            detail: detail.value,
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
            message.value = error.response.data.detail;
          }else{
            message.value = "問い合わせの送信に失敗しました";
          }
        }
      }
  
      return {
        category,
        detail,
        message,
        SendInquiry
      }
    }
  }
  </script>