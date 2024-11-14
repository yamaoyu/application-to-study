<template>
  <div style="white-space: pre-wrap;" v-if="message" class="message">
    <h3>月ごとの活動実績</h3>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
  <div v-if="activities.length > 0" class="activities">
    <h3>活動状況(日別)</h3>
    <ul v-for="(activity, index) in activities" :key="index" class="activity">
      <p>{{ activity.date }}</p>
      <p>目標時間:{{ activity.target_time }}時間 活動時間:{{ activity.actual_time }}時間 ステータス:{{ activity.is_achieved }}</p>
    </ul>
  </div>
  <form @submit.prevent="GetMonthlyInfo">
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
    <button type="submit">検索</button>
  </form>
  <div>
    <router-link to="/form/income">月収登録</router-link>
  </div>
  <div>
    <router-link to="/form/target">目標時間登録</router-link>
  </div>
  <div>
    <router-link to="/form/actual">活動時間登録</router-link>
  </div>
  <div>
    <router-link to="/finish/activity">活動を終了</router-link>
  </div>
  <div>
    <router-link to="/all">全期間の活動記録</router-link>
  </div>
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
    const year = ref("")
    const month = ref("")
    const message = ref("")
    const url = ref("")
    const router = useRouter()
    const activities = ref([])


    const GetMonthlyInfo = async() =>{
      try{
          url.value = 'http://localhost:8000/activities/' + year.value + '/' + month.value;
          const response = await axios.get(url.value)
          if (response.status===200){
            message.value = [`合計:${response.data.total_monthly_income}万円\n`,
                            `内訳\n`,
                            `月収:${response.data.salary}万円\n`,
                            `ボーナス合計:${response.data.total_bonus}万円\n`,
                            `目標達成日数:${response.data.success_days}日\n`,
                            `目標未達成日数:${response.data.fail_days}日`].join('');
            activities.value = response.data.activity_list;
          }
      } catch (error){
        if (error.response.status===401){
            router.push(
              {"path":"/login",
                "query":{message:"再度ログインしてください"}
              })
          }else if (error.response.status!==500){
            message.value = error.response.data.detail;
          }else{
            message.value = "情報の取得に失敗しました";
          }
      }
    }

    return {
      message,
      year,
      month,
      activities,
      GetMonthlyInfo
    }
  }
}
</script>