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
      <input type="button" value="-1" @click="decreaseOneYear">
      <input type="button" value="+1" @click="increaseOneYear">
      <div v-if="year_msg" class="year_msg">{{ year_msg }}</div>
    </div>
    <div>
      <label for="month">月:</label>
      <select id="month" v-model="month" required>
        <option v-for="month in monthOptions" :key="month">
          {{ month }}
        </option>
      </select>
      <input type="button" value="今月" @click="insertThisMonth">
      <input type="button" value="-1" @click="decreaseOneMonth">
      <input type="button" value="+1" @click="increaseOneMonth">
      <div v-if="month_msg" class="month_msg">{{ month_msg }}</div>
    </div>
    <div>
      <label for="monthlyIncome">月収(万):</label>
      <input type="number" id="monthlyIncome" v-model="monthlyIncome" required min="5" max="999">
      <input type="button" value="先月の給料" @click="insertPreviousSalary">
      <input type="button" value="-1" @click="updateSalary(-1)">
      <input type="button" value="+1" @click="updateSalary(1)">
      <input type="button" value="-5" @click="updateSalary(-5)">
      <input type="button" value="+5" @click="updateSalary(5)">
      <div v-if="salary_msg" class="salary_msg">{{ salary_msg }}</div>
    </div>
    <button type="submit">登録</button>
  </form>
  <div v-if="message" class="message">{{ message }}</div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { generateYearOptions, generateMonthOptions, changeMonth, changeYear } from './lib/index';
import { useAuthStore } from '@/store/authenticate';

export default {
  created() {
      this.yearOptions = generateYearOptions();
      this.monthOptions = generateMonthOptions();
    },

  setup() {
    const year = ref('')
    const month = ref('')
    const monthlyIncome = ref(5)
    const year_msg = ref('')
    const month_msg = ref('')
    const salary_msg = ref('')
    const message = ref('')
    const router = useRouter()
    const authStore = useAuthStore()
    const { insertThisYear, decreaseOneYear, increaseOneYear } = changeYear(year, year_msg);
    const { insertThisMonth, decreaseOneMonth, increaseOneMonth } = changeMonth(month, year, month_msg);
    
    const insertPreviousSalary = async() =>{
      // 先月の年収を取得
      const date = new Date()
      let prevYear = date.getFullYear()
      // 先月のデータを取得するため+1しない
      let prevMonth = date.getMonth()
      if (date.getMonth() == 0){
        prevYear = date.getFullYear() - 1
        prevMonth = 12
      } 
      try {
        const url = process.env.VUE_APP_BACKEND_URL + 'incomes/' + prevYear + '/' + prevMonth;
        const response = await axios.get(url, {headers: {Authorization: authStore.getAuthHeader}})
        if (response.status===200){
          monthlyIncome.value = response.data["今月の詳細"].salary
        } else {
          salary_msg.value = "先月の月収を取得できませんでした"
        }
      } catch (error) {
        switch (error.response.status){
          case 404:
            salary_msg.value = "先月の月収は登録されていません"
            break;
          default:
            salary_msg.value = "先月の月収を取得できませんでした";
        }
      }
    }

    const updateSalary = async(step) =>{
      if (step > 0){
        if   (monthlyIncome.value + step <= 999){
          monthlyIncome.value += step
          salary_msg.value = ""
        } else {
          monthlyIncome.value = 999
          salary_msg.value = "月収は999万円までとなります"
        }
      } else if (step < 0) {
        if  (monthlyIncome.value + step >= 5){
          monthlyIncome.value += step
          salary_msg.value = 0
        } else {
          monthlyIncome.value = 5
          salary_msg.value = "月収は5万円以上となります"
        }
      }
    }

    const registerSalary = async() =>{
        try {
          const url = process.env.VUE_APP_BACKEND_URL + 'incomes/'+ year.value + '/' + month.value;
          const response = await axios.post(url, 
                                            {salary: Number(monthlyIncome.value)},
                                            {headers: {Authorization: authStore.getAuthHeader}})
          if (response.status===201){
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
      monthlyIncome,
      year_msg,
      month_msg,
      salary_msg,
      message,
      insertThisYear,
      insertThisMonth,
      insertPreviousSalary,
      updateSalary,
      registerSalary,
      decreaseOneYear,
      increaseOneYear,
      decreaseOneMonth,
      increaseOneMonth
    }
  }
}

</script>