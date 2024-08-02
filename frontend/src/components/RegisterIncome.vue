<template>
  <h3>月収の登録</h3>
  <form @submit.prevent="RegisterIncome">
      <div>
        <label for="year">年:</label>
        <input type="text" id="year" v-model="year" required>
      </div>
      <div>
        <label for="month">月:</label>
        <input type="month" id="month" v-model="month" required>
      </div>
      <div>
        <label for="MonthlyIncome">月収(万):</label>
        <input type="MonthlyIncome" id="MonthlyIncome" v-model="MonthlyIncome" required>
      </div>
      <button type="submit">登録</button>
  </form>
  <div v-if="message" class="message">{{ message }}</div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const year = ref('')
    const month = ref('')
    const MonthlyIncome = ref('')
    const message = ref('')
    const router = useRouter()
    const year_month = ref('')
    

    const RegisterIncome = async() =>{
        try {
          year_month.value =  year.value + "-" + month.value
          const response = await axios.post('http://localhost:8000/income', {
            year_month: year_month.value,
            monthly_income: MonthlyIncome.value,
          })
          // ここでログイン後の処理を行う（例：トークンの保存、ページ遷移など）
          if (response.status===201){
            message.value = response.data.message
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
            message.value = "月収の登録に失敗しました";
          }
        }
      }

    return {
      year,
      month,
      year_month,
      MonthlyIncome,
      message,
      RegisterIncome
    }
  }
}
</script>