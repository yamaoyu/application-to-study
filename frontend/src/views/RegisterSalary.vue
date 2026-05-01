<template>
  <h3>月収の登録</h3>
  <form @submit.prevent="registerSalary(monthlyIncome)" class="form-inline">
    <div class="container col-8 d-flex justify-content-center">
      <div class="input-group">
        <input
          type="month"
          v-model="selectedMonth"
          :min="minMonth"
          :max="maxMonth"
          class="form-control col-2"
          data-testid="selected-month"
        />
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseYear(-1)"
          :disabled="isAtMinYear"
          data-testid="previousYear"
        >
          前年
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseMonth(-1)"
          :disabled="isAtMinMonth"
          data-testid="previousMonth"
        >
          前月
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseMonth(1)"
          :disabled="isAtMaxMonth"
          data-testid="nextMonth"
        >
          翌月
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="increaseYear(1)"
          :disabled="isAtMaxYear"
          data-testid="nextYear"
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
          max="2000"
          min="5"
          data-testid="income-form"
        />
        <span class="input-group-text">万円</span>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(-10)"
          :disabled="isMinIncome"
          data-testid="minus10"
        >
          -10万
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(-5)"
          :disabled="isMinIncome"
          data-testid="minus5"
        >
          -5万
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(5)"
          :disabled="isMaxIncome"
          data-testid="plus5"
        >
          +5万
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="updateSalary(10)"
          :disabled="isMaxIncome"
          data-testid="plus10"
        >
          +10万
        </button>
      </div>
    </div>

    <button type="submit" class="btn btn-outline-secondary mt-3" data-testid="submit">登録</button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="registerMsg" class="mt-3 p-3 col-8" :class="getResponseAlert(registerStatusCode)" data-testid="register-msg">{{ registerMsg }}</p>
    <p v-else-if="queryMsg" class="mt-3 p-3 col-8" :class="getResponseAlert(404)" data-testid="query-msg">{{ queryMsg }}</p>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getMaxMonth, changeMonth, changeYear } from '@/views/utils/date';
import { getResponseAlert } from './utils/ui';
import { useFetchMonthlySalary, useRegisterSalary } from './composables/useSalary';

export default {
  setup() {
    const route = useRoute();
    const queryMsg = ref("");
    const minMonth = "2024-01";
    const maxMonth = getMaxMonth();
    const monthlyIncome = ref(null);
    const { fetchRes, fetchMonthlySalary } = useFetchMonthlySalary();
    const { registerMsg, selectedMonth, registerStatusCode, registerSalary } = useRegisterSalary();
    const isAtMinMonth = computed(() => selectedMonth.value <= minMonth);
    const isAtMaxMonth = computed(() => selectedMonth.value >= maxMonth);
    const isAtMinYear = computed(() => selectedMonth.value <= "2024-12");
    const isAtMaxYear = computed(() => selectedMonth.value >= maxMonth.split("-")[0]);
    const isMinIncome = computed(() => monthlyIncome.value <= 5);
    const isMaxIncome = computed(() => monthlyIncome.value >= 2000);
    const { increaseYear } = changeYear(selectedMonth);
    const { increaseMonth } = changeMonth(selectedMonth);

    const updateSalary = async(step) =>{
      // 画面に表示される給料を更新する関数
      if (step > 0){
        monthlyIncome.value = Math.min(monthlyIncome.value + step, 2000)
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
      await fetchMonthlySalary(year, month);
      if (fetchRes.value?.status === 200) {
        monthlyIncome.value = fetchRes.value.data["month_info"].salary;
      } else {
        monthlyIncome.value = 5;
      };
      // クエリパラメータにメッセージがある場合はそちらで上書きする
      if (typeof route.query.incomeMsg === 'string') {
        queryMsg.value = route.query.incomeMsg;
      };
    }
  );

    return {
      monthlyIncome,
      registerMsg,
      registerStatusCode,
      queryMsg,
      getResponseAlert,
      updateSalary,
      registerSalary,
      minMonth,
      maxMonth,
      selectedMonth,
      isAtMinMonth,
      isAtMaxMonth,
      isAtMinYear,
      isAtMaxYear,
      isMinIncome,
      isMaxIncome,
      increaseYear,
      increaseMonth
    }
  }
}

</script>