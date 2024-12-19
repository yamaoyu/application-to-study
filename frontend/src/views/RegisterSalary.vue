<template>
  <h3>月収の登録</h3>
  <form @submit.prevent="registerSalary">
    <div>
      <label for="year">年:</label>
      <select v-model="year" required>
        <option v-for="year in yearOptions" :key="year">
          {{ year }}
        </option>
      </select>
      <input type="button" value="今年" @click="insertThisYear">
    </div>
    <div>
      <label for="month">月:</label>
      <select id="month" v-model="month" required>
        <option v-for="month in monthOptions" :key="month">
          {{ month }}
        </option>
      </select>
      <input type="button" value="今月" @click="insertThisMonth">
    </div>
    <div>
      <label for="MonthlyIncome">月収(万):</label>
      <input type="number" id="MonthlyIncome" v-model="MonthlyIncome" required>
    </div>
    <button type="submit">登録</button>
  </form>
  <div v-if="message" class="message">{{ message }}</div>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { generateYearOptions } from './lib/index';
import { generateMonthOptions } from './lib/index';
import store from '@/store';

export default {
  created() {
      this.yearOptions = generateYearOptions();
      this.monthOptions = generateMonthOptions();
    },

  setup() {
    const year = ref('')
    const month = ref('')
    const MonthlyIncome = ref('')
    const message = ref('')
    const router = useRouter()

    const insertThisYear = async() =>{
      year.value = new Date().getFullYear()
    }

    const insertThisMonth = async() =>{
      month.value = new Date().getMonth()+1
    }
    

    const registerSalary = async() =>{
        try {
          const url = process.env.VUE_APP_BACKEND_URL + 'incomes/'+ year.value + '/' + month.value;
          const response = await axios.post(url, 
                                            {salary: Number(MonthlyIncome.value)},
                                            {headers: {Authorization: `${store.state.tokenType} ${store.state.accessToken}`}})
          if (response.status===201){
            message.value = response.data.message
          }
        } catch (error) {
          if (error.response){
            console.log(error.response.data)
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
                message.value =  "月収の登録に失敗しました"
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
      year,
      month,
      MonthlyIncome,
      message,
      insertThisYear,
      insertThisMonth,
      registerSalary
    }
  }
}
</script>