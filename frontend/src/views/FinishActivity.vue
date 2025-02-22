<template>
  <div class="container">
    <h2>活動を終了</h2>
    <div class="row">
      <form @submit.prevent="finishActivity">
        <div class="input-group col-10">
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
      <p v-if="fin_msg" class="mt-3 col-10" :class="responseAlertClass(statusCode)">{{ fin_msg }}</p>
    </div>
  </div>
  <div class="container">
    <h3 class="mt-4">{{ date }}の実績</h3>
    <div class="row mt-3" v-if="activity_res">
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">目標時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activity_res.data.target_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">活動時間</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center">{{ activity_res.data.actual_time }}</span>
            時間
          </div>
        </div>
      </div>
      <div class="col-4">
        <div class="bg-white p-4 rounded shadow">
          <h3 class="small">ステータス</h3>
          <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-center" :class="statusClass[activity_res.data.status]">{{ STATUS_DICT[activity_res.data.status] }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="check_msg" class="row d-flex justify-content-center mt-3">
      <p class="alert alert-warning">{{ check_msg }}</p>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { changeDate, STATUS_DICT, statusClass, responseAlertClass } from './lib/index';

export default {
  setup() {
    const date = ref(new Date().toISOString().slice(0, 10)); // 今日の日付を取得
    const fin_msg = ref("")
    const check_msg = ref("")
    const router = useRouter()
    const statusCode = ref()
    const activity_res = ref()
    const authStore = useAuthStore()
    const { increaseDay } = changeDate(date, fin_msg);

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
          statusCode.value = response.status
          if (response.status===200){
            fin_msg.value = response.data.fin_msg
          }
        } catch (error) {
          statusCode.value = error.response.status
          if (error.response){
            switch (error.response.status){
            case 401:
            router.push(
              {"path":"/login",
                "query":{fin_msg:"再度ログインしてください"}
              })
              break;
            case 422:
              fin_msg.value = error.response.data.detail;
              break;
            case 500:
              fin_msg.value =  "活動の確定に失敗しました"
              break;
            default:
              fin_msg.value = error.response.data.detail;
            }
          } else if (error.request){
            fin_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            fin_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
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
        activity_res.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        check_msg.value = ""
      } catch (error) {
        activity_res.value = ""
        if (error.response){
          switch (error.response.status){
          case 401:
          router.push(
            {"path":"/login",
              "query":{check_msg:"再度ログインしてください"}
            })
            break;
          case 422:
            check_msg.value = error.response.data.detail;
            break;
          case 500:
            check_msg.value =  "活動の取得に失敗しました"
            break;
          default:
            check_msg.value = error.response.data.detail;
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
      fin_msg,
      check_msg,
      statusCode,
      activity_res,
      finishActivity,
      increaseDay,
      STATUS_DICT,
      statusClass,
      responseAlertClass
    }
  }
}
</script>