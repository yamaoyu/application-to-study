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
        <option v-for="year in yearOptions" :key="year">
          {{ year }}
        </option>
      </select>
    </div>
    <div>
      <label for="month">月:</label>
      <select id="month" v-model="month" required>
        <option v-for="month in monthOptions" :key="month">
          {{ month }}
        </option>
      </select>
    </div>
    <button type="submit">検索</button>
  </form>
  <div>
    <router-link to="/register/salary">月収登録</router-link>
  </div>
  <div>
    <router-link to="/register/target">目標時間登録</router-link>
  </div>
  <div>
    <router-link to="/register/actual">活動時間登録</router-link>
  </div>
  <div>
    <router-link to="/finish/activity">活動を終了</router-link>
  </div>
  <div>
    <router-link to="/view/all-activities">全期間の活動記録</router-link>
  </div>
  <div>
    <router-link to="/home">ホームへ戻る</router-link>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { generateYearOptions } from './lib/index';
import { generateMonthOptions } from './lib/index';
import store from '@/store';


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


    const GetMonthlyInfo = async() =>{
      try{
          const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value + '/' + month.value;
          const response = await axios.get(url,
                                          {headers: {Authorization: `${store.state.tokenType} ${store.state.accessToken}`}})
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
                message.value =  "情報の取得に失敗しました"
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
      message,
      year,
      month,
      activities,
      GetMonthlyInfo
    }
  }
}
</script>