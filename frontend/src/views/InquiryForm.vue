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
          if (error.response){
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
                message.value =  "問い合わせの送信に失敗しました"
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
        category,
        detail,
        message,
        SendInquiry
      }
    }
  }
  </script>