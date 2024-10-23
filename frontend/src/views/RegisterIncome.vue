<template>
  <h3>月収の登録</h3>
  <form @submit.prevent="RegisterIncome">
    <div>
      <label for="year">年:</label>
      <select id="year" v-model="year" required>
        <option value="">-</option>
        <option value="2024">2024</option>
        <option value="2025">2025</option>
        <option value="2026">2026</option>
        <option value="2027">2027</option>
        <option value="2028">2028</option>
      </select>
    </div>
    <div>
      <label for="month">月:</label>
      <select id="month" v-model="month" required>
        <option value="">-</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5">5</option>
        <option value="6">6</option>
        <option value="7">7</option>
        <option value="8">8</option>
        <option value="9">9</option>
        <option value="10">10</option>
        <option value="11">11</option>
        <option value="12">12</option>
      </select>
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

export default {
  setup() {
    const year = ref('')
    const month = ref('')
    const MonthlyIncome = ref('')
    const message = ref('')
    const router = useRouter()
    

    const RegisterIncome = async() =>{
        try {
          const response = await axios.post('http://localhost:8000/earnings', {
            year: year.value,
            month: month.value,
            monthly_income: MonthlyIncome.value,
          })
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
      MonthlyIncome,
      message,
      RegisterIncome
    }
  }
}
</script>