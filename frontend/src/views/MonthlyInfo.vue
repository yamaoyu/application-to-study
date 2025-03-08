<template>
  <h2 v-if="!response">月ごとの活動実績</h2>
  <h2 v-else>{{ selectedMonth.split("-")[0] }}年{{ selectedMonth.split("-")[1] }}月の活動実績</h2>
  <div class="container" v-if="response">
    <div class="row justify-content-center mb-4">
      <div class="col-8">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(response)" class="h3 fw-bold text-center">{{ response.data.total_monthly_income }}</span>
            万円
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">月収</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold">{{ response.data.salary }}</span>
            <span class="small">万円</span>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス+ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(response)" class="h3 fw-bold">{{ response.data.pay_adjustment }}</span>
            <span class="small">万円</span>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ボーナス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-success">{{ response.data.bonus }}</span>
            <span class="small">万円</span>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ペナルティ</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-danger">{{ response.data.penalty }}</span>
            <span class="small">万円</span>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">達成日数</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-success">{{ response.data.success_days }}</span>
            <span class="small">日</span>
          </div>
        </div>
      </div>
      <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">未達成日数</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-danger">{{ response.data.fail_days }}</span>
            <span class="small">日</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <br>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="col-8 alert alert-warning">{{ message }}</p>
  </div>
  <div v-if="activities.length > 0" class="activities">
    <h2>活動状況(日別)</h2>
    <table class="table table-striped table-responsive">
      <thead class="table-dark">
        <tr>
          <th>日付</th>
          <th>目標時間</th>
          <th>活動時間</th>
          <th>ステータス</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(activity, index) in activities" :key="index">
          <td>{{ activity.date }}</td>
          <td>{{ activity.target_time }}時間</td>
          <td>{{ activity.actual_time }}時間</td>
          <td :class="getStatusColors[activity.status]">{{ STATUS_DICT[activity.status] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <form @submit.prevent="GetMonthlyInfo" class="form-inline">
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
    <button type="submit" class="btn btn-outline-secondary mt-2">検索</button>
  </form>
</template>

<script>
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { getMaxMonth, changeMonth, changeYear, STATUS_DICT, getStatusColors, getAdjustmentColors, getThisMonth, verfiyRefreshToken, getMonthlyinfoError } from './lib/index';
import { useAuthStore } from '@/store/authenticate';
import "../assets/styles/common.css";
import { jwtDecode } from 'jwt-decode';


export default {
  setup() {
    const message = ref("")
    const router = useRouter()
    const activities = ref([])
    const response = ref()
    const authStore = useAuthStore()
    const selectedMonth = ref(getThisMonth());
    const minMonth = "2024-01";
    const maxMonth = getMaxMonth();
    const isAtMinMonth = computed(() => selectedMonth.value <= minMonth)
    const isAtMaxMonth = computed(() => selectedMonth.value >= maxMonth)
    const isAtMinYear = computed(() => selectedMonth.value <= "2024-12")
    const isAtMaxYear = computed(() => selectedMonth.value >= maxMonth.split("-")[0])
    const { increaseYear } = changeYear(selectedMonth);
    const { increaseMonth } = changeMonth(selectedMonth);
    const { handleError } = getMonthlyinfoError(response, activities, message, router);

    const sendRequestForMonthlyInfo = async() =>{
      const [year, month] = selectedMonth.value.split('-').map(Number)
      const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month;
      response.value = await axios.get(url,
                                      {headers: {Authorization: authStore.getAuthHeader}})
      if (response.value.status===200){
        activities.value = response.value.data.activity_list;
        message.value = ""
      } 
    }

    const GetMonthlyInfo = async() =>{
      // 検索ボタンが押された時の処理
      try{
        await sendRequestForMonthlyInfo();
      } catch (error){
        if (error.response?.status === 401) {
          try {
            // リフレッシュトークンを検証して新しいアクセストークンを取得
            const tokenResponse = await verfiyRefreshToken();
            // 新しいアクセストークンをストアに保存
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await sendRequestForMonthlyInfo();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          handleError(error)
        }
      }
    }

    return {
      message,
      response,
      getStatusColors,
      getAdjustmentColors,
      activities,
      GetMonthlyInfo,
      STATUS_DICT,
      selectedMonth,
      minMonth,
      maxMonth,
      isAtMinMonth,
      isAtMaxMonth,
      isAtMinYear,
      isAtMaxYear,
      increaseYear,
      increaseMonth
    }
  }
}
</script>