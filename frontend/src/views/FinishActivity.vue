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
import { changeDate, STATUS_DICT, getStatusColors,
          getResponseAlert, getActivityAlert, getToday,
          verifyRefreshToken, finishActivityError, getActivityError } from './lib/index';
import { jwtDecode } from 'jwt-decode';

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
    const { handleError: handleFinishError } = finishActivityError(activityStatus, finMsg, router);
    const { handleError: handleActivityError } = getActivityError(activityRes, checkMsg, router);

    const sendFinishRequest = async() => {
      /**
       * 活動終了リクエストを送信する関数 
       */
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
    }

    const finishActivity = async() =>{
      // 活動終了ボタンがクリックされたときに実行される
      try {
        await sendFinishRequest();
        // 更新後の活動情報を取得
        await checkActivity();
      } catch (error) {
        if (error.response?.status === 401) {
          // リフレッシュトークンを検証して新しいアクセストークンを取得
          try {
            const tokenResponse = await verifyRefreshToken();
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await sendFinishRequest();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          handleFinishError(error)
        }
      }
    }
    
    const getActivity = async() => {
      // 活動情報を取得リクエストを送信する関数
      const dateParts = date.value.split('-');
      const year = dateParts[0];
      let month = dateParts[1];
      let day = dateParts[2];
      const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day;
      activityRes.value = await axios.get(url,
                                      {headers: {Authorization: authStore.getAuthHeader}})
      checkMsg.value = ""
    }

    const checkActivity = async() =>{
      // 日付が変更された時と終了ボタンがクリックされた時に実行される
      try {
        await getActivity();
      } catch (error) {
        if (error.response?.status === 401) {
          // リフレッシュトークンを検証して新しいアクセストークンを取得
          try {
            const tokenResponse = await verifyRefreshToken();
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await getActivity();
          } catch (refreshError) {
            router.push({
              path: "/login",
              query: { message: "再度ログインしてください" }
            });
          }            
        } else {
          handleActivityError(error)
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