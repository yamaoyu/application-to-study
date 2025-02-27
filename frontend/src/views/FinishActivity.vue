<template>
  <div class="container col-8">
    <h2>活動を終了</h2>
    <div class="row">
      <form @submit.prevent="finishActivity">
        <div class="input-group">
          <span class="col-2 p-2 input-group-text">日付</span>
          <input
            type="date"
            v-model="date"
            min="2024-01-01"
            class="form-control col-2"
          />
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="increaseDay(-1)"
            >
            前日
          </button>
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="increaseDay(1)"
            >
            翌日
          </button>
        </div>
        <button type="submit" class="btn btn-outline-secondary mt-3">終了</button>
      </form>
    </div>
    <div class="row d-flex justify-content-center">
      <p v-if="finMsg" class="mt-3" :class="getActivityAlert(activityStatus)">{{ finMsg }}</p>
    </div>
  </div>
  <div class="container">
    <h3 class="mt-4">{{ date }}の実績</h3>
    <div class="row mt-3" v-if="activityRes">
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">目標時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activityRes.data.target_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">活動時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activityRes.data.actual_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ステータス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center" :class="getStatusColors[activityRes.data.status]">{{ STATUS_DICT[activityRes.data.status] }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="checkMsg" class="row d-flex justify-content-center mt-3">
      <p class="alert alert-warning col-8">{{ checkMsg }}</p>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { changeDate, STATUS_DICT, getStatusColors, getResponseAlert, getActivityAlert, getToday } from './lib/index';

export default {
  setup() {
    const date = ref(getToday()); // 今日の日付を取得
    const finMsg = ref("")
    const checkMsg = ref("")
    const router = useRouter()
    const activityRes = ref()
    const activityStatus = ref("")
    const authStore = useAuthStore()
    const { increaseDay } = changeDate(date, finMsg);

    const finishActivity = async() =>{
        try {
          // 日付から年月日を取得
          const dateParts = date.value.split('-');
          const year = dateParts[0];
          let month = dateParts[1];
          let day = dateParts[2];
          // 月と日が一桁の場合、表記を変更 例)09→9
          month = parseInt(month, 10);
          day = parseInt(day, 10);
          const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day + '/finish';
          // axiosのputの第二引数はリクエストボディとなるため{}を用意する。(リクエストボディで渡すデータはないため空)
          const response = await axios.put(url,
                                          {},
                                          {headers: {Authorization: authStore.getAuthHeader}})
          if (response.status===200){
            activityStatus.value = response.data.status;
            finMsg.value = response.data.message;
          }
        } catch (error) {
          activityStatus.value = ""
          if (error.response){
            switch (error.response.status){
            case 401:
            router.push(
              {"path":"/login",
                "query":{finMsg:"再度ログインしてください"}
              })
              break;
            case 422:
              finMsg.value = error.response.data.detail;
              break;
            case 500:
              finMsg.value =  "活動の確定に失敗しました"
              break;
            default:
              finMsg.value = error.response.data.detail;
            }
          } else if (error.request){
            finMsg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            finMsg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
        }
      }
    
    const checkActivity = async() =>{
      try {
        const dateParts = date.value.split('-');
        const year = dateParts[0];
        let month = dateParts[1];
        let day = dateParts[2];
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day;
        activityRes.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        checkMsg.value = ""
      } catch (error) {
        activityRes.value = ""
        if (error.response){
          switch (error.response.status){
          case 401:
          router.push(
            {"path":"/login",
              "query":{checkMsg:"再度ログインしてください"}
            })
            break;
          case 422:
            checkMsg.value = error.response.data.detail;
            break;
          case 500:
            checkMsg.value =  "活動の取得に失敗しました"
            break;
          default:
            checkMsg.value = error.response.data.detail;
          }
        }
      }
    }

    watch(date, () => {
      checkActivity();
    });

    onMounted(() => {
      checkActivity();
    });

    return {
      date,
      finMsg,
      checkMsg,
      activityRes,
      activityStatus,
      finishActivity,
      increaseDay,
      STATUS_DICT,
      getStatusColors,
      getResponseAlert,
      getActivityAlert
    }
  }
}
</script>