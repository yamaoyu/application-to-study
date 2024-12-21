<template>
  <h3>活動を終了</h3>
  <form @submit.prevent="finishActivity">
    <div>
      <label for="date">日付:</label>
      <input type="date" id="date" v-model="date" required>
      <input type="button" value="今日" @click="insertToday">
    </div>
    <button type="submit">終了</button>
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
import store from '@/store';

export default {
  setup() {
    const year = ref("")
    const month = ref("")
    const day = ref("")
    const date = ref("")
    const message = ref("")
    const router = useRouter()

    const insertToday = async() =>{
      const today = new Date()
      date.value = `${today.getFullYear()}-${today.getMonth()+1}-${today.getDate()}`
    }

    const finishActivity = async() =>{
        try {
          // 日付から年月日を取得
          const dateParts = date.value.split('-');
          year.value = dateParts[0];
          month.value = dateParts[1];
          day.value = dateParts[2];
          // 月と日が一桁の場合、表記を変更 例)09→9
          month.value = parseInt(month.value, 10);
          day.value = parseInt(day.value, 10);
          const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value + '/' + month.value + '/' + day.value + '/finish';
          // axiosのputの第二引数はリクエストボディとなるため{}を用意する。(リクエストボディで渡すデータはないため空)
          const response = await axios.put(url,
                                          {},
                                          {headers: {Authorization: `${store.state.authenticateModule["tokenType"]} ${store.state.authenticateModule["accessToken"]}`}})
          if (response.status===200){
            message.value = response.data.message
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
              message.value =  "活動の確定に失敗しました"
              break;
            default:
              message.value = error.response.data.detail;
            }
          } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }

    return {
      year,
      month,
      day,
      date,
      message,
      insertToday,
      finishActivity
    }
  }
}
</script>