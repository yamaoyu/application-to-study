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
    <p v-if="incomeMsg" class="mt-3 p-3 col-8" :class="getResponseAlert(statusCode)">{{ incomeMsg }}</p>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { getMaxMonth, changeMonth, changeYear, getResponseAlert, getThisMonth, getIncomeByMonth, registerMonthlyIncome } from './lib/index';

export default {
  setup() {
    const monthlyIncome = ref();
    const incomeRes = ref();
    const statusCode = ref();
    const incomeMsg = ref('');
    const minMonth = "2024-01";
    const maxMonth = getMaxMonth();
    const selectedMonth = ref(getThisMonth());
    const isAtMinMonth = computed(() => selectedMonth.value <= minMonth);
    const isAtMaxMonth = computed(() => selectedMonth.value >= maxMonth);
    const isAtMinYear = computed(() => selectedMonth.value <= "2024-12");
    const isAtMaxYear = computed(() => selectedMonth.value >= maxMonth.split("-")[0]);
    const isMinInome = computed(() => monthlyIncome.value <= 5);
    const isMaxIncome = computed(() => monthlyIncome.value >= 999);
    const { increaseYear } = changeYear(selectedMonth);
    const { increaseMonth } = changeMonth(selectedMonth);
    const registerSalary = registerMonthlyIncome(selectedMonth, monthlyIncome, incomeMsg, statusCode);

    const updateSalary = async(step) =>{
      // 画面に表示される給料を更新する関数
      if (step > 0){
        monthlyIncome.value = Math.min(monthlyIncome.value + step, 999)
      } else if (step < 0) {
        monthlyIncome.value = Math.max(monthlyIncome.value + step, 5)
      }
    };

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
      const getMonthlyIncome = getIncomeByMonth(incomeRes, incomeMsg, year, month);
      await getMonthlyIncome();
      if (incomeRes.value?.status===200){
        monthlyIncome.value = incomeRes.value.data["month_info"].salary
      } else {
        monthlyIncome.value = 5
      }
    }
  );

    return {
      monthlyIncome,
      statusCode,
      getResponseAlert,
      incomeMsg,
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