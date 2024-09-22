<template>
  <h3>月ごとの活動実績</h3>
  <div>
    <p v-if="message" class="message">{{ message }}</p>
    <p v-if="year" class="year">{{ year }}</p>
    <p v-if="month" class="month">{{ month }}</p>
  </div>
  <form @submit.prevent="GetMonthlyInfo">
      <div>
        <label for="year">年:</label>
        <input type="text" id="year" v-model="year" required>
      </div>
      <div>
        <label for="month">月:</label>
        <input type="text" id="month" v-model="month" required>
      </div>
      <button type="submit">検索</button>
  </form>
  <div>
    <router-link to="/form/income">月収登録</router-link>
  </div>
  <div>
    <router-link to="/form/target">目標時間登録</router-link>
  </div>
  <div>
    <router-link to="/form/actual">活動時間登録</router-link>
  </div>
  <div>
    <router-link to="/finish/activity">活動を終了</router-link>
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
    const year = ref("")
    const month = ref("")
    const message = ref("")
    const url = ref("")
    const router = useRouter()


    const GetMonthlyInfo = async() =>{
      try{
          url.value = 'http://localhost:8000/activities/' + year.value + '/' + month.value;
          const response = await axios.get(url.value)
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===200){
            message.value = response.data
          }
      } catch (error){
        if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if (error.response.status!==500){
            message.value = error.response.data.detail;
          }else{
            message.value = "情報の取得に失敗しました";
          }
      }
    }

    return {
      message,
      year,
      month,
      GetMonthlyInfo
    }
  }
}
</script>