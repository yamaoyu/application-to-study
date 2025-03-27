<template>
  <h2 v-if="!response">年ごとの活動実績</h2>
  <h2 v-else>{{ year }}年の活動実績</h2>
  <div class="container" v-if="response">
    <div class="row justify-content-center mb-4">
      <div class="col-8">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(response)" class="h3 fw-bold text-center">{{ response.data.total_annual_income }}</span>
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
            <span class="h3 fw-bold">{{ response.data.annual_income }}</span>
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
  <div v-if="Object.keys(activities).length > 0" class="activities mt-3">
    <h2>内訳(月別)</h2>
    <table class="table table-striped table-responsive">
      <thead class="table-dark">
        <tr>
          <th>月</th>
          <th>給料</th>
          <th>ボーナス</th>
          <th>ペナルティ</th>
          <th>達成</th>
          <th>未達成</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(activity, index) in activities" :key="index">
          <td class="fw-bold">{{ MONTH_DICT[index] }}</td>
          <td v-if="activity.salary" class="fw-bold">{{ activity.salary }}万円</td>
          <td v-else>未登録</td>
          <td v-if="activity.bonus" class="fw-bold text-center text-success">{{ activity.bonus }}万円</td>
          <td v-else></td>
          <td v-if="activity.penalty" class="fw-bold text-center text-danger">{{ activity.penalty }}万円</td>
          <td v-else></td>
          <td v-if="activity.success_days" class="fw-bold text-center text-success">{{ activity.success_days }}日</td>
          <td v-else></td>
          <td v-if="activity.fail_days" class="fw-bold text-center text-danger">{{ activity.fail_days }}日</td>
          <td v-else></td>
        </tr>
      </tbody>
    </table>
  </div>
  <form @submit.prevent="GetMonthlyInfo" class="form-inline">
    <div class="container col-8 d-flex justify-content-center">
      <div class="input-group">
        <input
          type="year"
          v-model="year"
          :min="minYear"
          :max="maxYear"
          class="form-control col-2"
        />
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="year-=1"
          :disabled="isAtMinYear"
        >
          前年
        </button>
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          @click="year+=1"
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
import { MONTH_DICT, getMaxYear, STATUS_DICT, getStatusColors, getAdjustmentColors, getThisYear, verifyRefreshToken } from './lib/index';
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
    const year = ref(getThisYear());
    const minYear = "2024";
    const isAtMinYear = computed(() => year.value <= "2024")
    const maxYear = getMaxYear();
    const isAtMaxYear = computed(() => year.value >= maxYear)

    const sendRequestForMonthlyInfo = async() =>{
      const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value;
      response.value = await axios.get(url,
                                      {headers: {Authorization: authStore.getAuthHeader}})
      if (response.value.status===200){
        activities.value = response.value.data.monthly_info;
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
            const tokenResponse = await verifyRefreshToken();
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
          console.log(error)
        }
      }
    }

    return {
      MONTH_DICT,
      message,
      response,
      getStatusColors,
      getAdjustmentColors,
      activities,
      GetMonthlyInfo,
      STATUS_DICT,
      year,
      minYear,
      maxYear,
      isAtMinYear,
      isAtMaxYear
    }
  }
}
</script>