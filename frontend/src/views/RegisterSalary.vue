<template>
  <h3>月収の登録</h3>
  <form @submit.prevent="registerSalary" class="form-inline">
    <div class="container col-8 d-flex justify-content-center">
      <div class="input-group">
        <input
          type="month"
          v-model="selectedMonth"
          :min="minMonth"
          :max="maxMonth"
          class="form-control col-2"
        />
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseYear(-1)"
          :disabled="isAtMinYear"
        >
          前年
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseMonth(-1)"
          :disabled="isAtMinMonth"
        >
          前月
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseMonth(1)"
          :disabled="isAtMaxMonth"
        >
          翌月
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseYear(1)"
          :disabled="isAtMaxYear"
        >
          翌年
        </button>
      </div>
    </div>
    <div class="container col-8 d-flex justify-content-center mt-3">
      <div class="input-group">
        <input
          type="number"
          v-model="monthlyIncome"
          class="form-control"
          placeholder="月収(万円)"
        />
        <span class="input-group-text">万円</span>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(-10)"
          :disabled="isMinInome"
        >
          -10万
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(-5)"
          :disabled="isMinInome"
        >
          -5万
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(5)"
          :disabled="isMaxIncome"
        >
          +5万
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(10)"
          :disabled="isMaxIncome"
        >
          +10万
        </button>
      </div>
    </div>

    <button type="submit" class="btn btn-outline-secondary mt-3">登録</button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 p-3 col-8" :class="responseAlertClass(statusCode)">{{ message }}</p>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { getMaxMonth, changeMonth, changeYear, responseAlertClass } from './lib/index';
import { useAuthStore } from '@/store/authenticate';

export default {
  setup() {
    const monthlyIncome = ref()
    const statusCode = ref()
    const message = ref('')
    const router = useRouter()
    const authStore = useAuthStore()
    const minMonth = "2024-01";
    const maxMonth = getMaxMonth();
    const selectedMonth = ref(new Date().toISOString().slice(0, 7));
    const isAtMinMonth = computed(() => selectedMonth.value <= minMonth)
    const isAtMaxMonth = computed(() => selectedMonth.value >= maxMonth)
    const isAtMinYear = computed(() => selectedMonth.value <= "2024-12")
    const isAtMaxYear = computed(() => selectedMonth.value >= maxMonth.split("-")[0])
    const isMinInome = computed(() => monthlyIncome.value <= 5)
    const isMaxIncome = computed(() => monthlyIncome.value >= 999)
    const { increaseYear } = changeYear(selectedMonth);
    const { increaseMonth } = changeMonth(selectedMonth);

    const updateSalary = async(step) =>{
      if (step > 0){
        monthlyIncome.value = Math.min(monthlyIncome.value + step, 999)
      } else if (step < 0) {
        monthlyIncome.value = Math.max(monthlyIncome.value + step, 5)
      }
    }

    const registerSalary = async() =>{
        try {
          const url = process.env.VUE_APP_BACKEND_URL + 'incomes/'+ selectedMonth.value.split("-")[0] + '/' + selectedMonth.value.split("-")[1];
          const response = await axios.post(url, 
                                            {salary: Number(monthlyIncome.value)},
                                            {headers: {Authorization: authStore.getAuthHeader}})
          statusCode.value = response.status
          if (response.status===201){
            message.value = response.data.message
          }
        } catch (error) {
          statusCode.value = error.response.status
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

    onMounted( async() =>{
      // 先月の年収を取得
      const date = new Date()
      let year = date.getFullYear()
      // 先月のデータを取得するため+1しない
      let month = date.getMonth()
      if (date.getMonth() == 0){
        year = date.getFullYear() - 1
        month = 12
      } 
      try {
        const url = process.env.VUE_APP_BACKEND_URL + 'incomes/' + year + '/' + month;
        const response = await axios.get(url, {headers: {Authorization: authStore.getAuthHeader}})
        if (response.status===200){
          monthlyIncome.value = response.data["month_info"].salary
        } else {
          monthlyIncome.value = 5
        }
      } catch (error) {
        monthlyIncome.value = 5
      }
    }
  )

    return {
      monthlyIncome,
      statusCode,
      responseAlertClass,
      message,
      updateSalary,
      registerSalary,
      minMonth,
      maxMonth,
      selectedMonth,
      isAtMinMonth,
      isAtMaxMonth,
      isAtMinYear,
      isAtMaxYear,
      isMinInome,
      isMaxIncome,
      increaseYear,
      increaseMonth
    }
  }
}

</script>