<template>
  <h3>月収の登録</h3>
  <form @submit.prevent="RegisterSalary">
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
    const url = ref('')
    const router = useRouter()
    

    const RegisterSalary = async() =>{
        try {
          url.value = 'http://localhost:8000/incomes/'+ year.value + '/' + month.value;
          const response = await axios.post(url.value, {
            year: year.value,
            month: month.value,
            salary: MonthlyIncome.value,
          })
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
                message.value = error.response.data.error;
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
      url,
      RegisterSalary
    }
  }
}
</script>