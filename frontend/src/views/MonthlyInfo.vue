<template>
  <h2 v-if="!response">月ごとの活動実績</h2>
  <h2 v-if="response">{{ year }}年{{ month }}月の活動実績</h2>
  <div class="container p-4" v-if="response">
    <div class="row justify-content-center mb-4">
      <div class="col-8 ">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">合計</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span :class="resultClass(response)" class="h3 fw-bold text-center">{{ response.data.total_monthly_income }}</span>
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
            <span :class="resultClass(response)" class="h3 fw-bold">{{ response.data.pay_adjustment }}</span>
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
          <h3 class="small">失敗日数</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-danger">{{ response.data.fail_days }}</span>
            <span class="small">日</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <br>
  <div v-if="message" class="message">
    <p v-if="message" class="message">{{ message }}</p>
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
          <td :class="statusClass[activity.status]">{{ STATUS_DICT[activity.status] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <form @submit.prevent="GetMonthlyInfo">
    <div>
      <label for="year">年:</label>
      <select id="year" v-model="year" required>
        <option v-for="year in yearOptions" :key="year">
          {{ year }}
        </option>
      </select>
      <input type="button" value="今年" @click="insertThisYear">
      <input type="button" value="-1" @click="decreaseOneYear">
      <input type="button" value="+1" @click="increaseOneYear">
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
    </div>
    <button type="submit" class="btn btn-outline-secondary">検索</button>
  </form>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { generateYearOptions, generateMonthOptions, changeMonth, changeYear, STATUS_DICT, statusClass, resultClass } from './lib/index';
import { useAuthStore } from '@/store/authenticate';
import "../assets/styles/common.css"


export default {
  created() {
      this.yearOptions = generateYearOptions();
      this.monthOptions = generateMonthOptions();
    },

  setup() {
    const year = ref("")
    const month = ref("")
    const message = ref("")
    const router = useRouter()
    const activities = ref([])
    const response = ref()
    const authStore = useAuthStore()
    const { insertThisYear, decreaseOneYear, increaseOneYear } = changeYear(year, message);
    const { insertThisMonth, decreaseOneMonth, increaseOneMonth } = changeMonth(month, year, message);

    const GetMonthlyInfo = async() =>{
      try{
          const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value + '/' + month.value;
          response.value = await axios.get(url,
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (response.value.status===200){
            activities.value = response.value.data.activity_list;
          }
      } catch (error){
        if (error.response.value){
          activities.value = []
          switch (error.response.value.status){
              case 401:
              router.push(
                {"path":"/login",
                  "query":{message:"再度ログインしてください"}
                })
                break;
              case 422:
                message.value = error.response.value.data.detail;
                break;
              case 500:
                message.value =  "情報の取得に失敗しました"
                break;
              default:
                message.value = error.response.value.data.detail;}
          } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
      }
    }

    return {
      message,
      year,
      month,
      response,
      statusClass,
      resultClass,
      activities,
      insertThisYear,
      insertThisMonth,
      GetMonthlyInfo,
      decreaseOneYear,
      increaseOneYear,
      decreaseOneMonth,
      increaseOneMonth,
      STATUS_DICT
    }
  }
}
</script>