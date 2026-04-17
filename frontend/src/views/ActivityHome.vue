<template>
    <div class="container">
        <div class="d-flex mb-3 align-items-baseline justify-content-center">
            <BButton 
                v-for="tab in tabs" 
                :key="tab.value"
                @click="activeTab = tab.value"
                :variant="activeTab === tab.value ? 'primary' : 'outline-secondary'"
                class="me-2"
                :title="`${tab.label}登録フォームへ切り替え`"
                :data-testid="tab.value"
            >
                {{ tab.label }}
            </BButton>
        </div>

        <div class="container">
            <h3 class="mt-5">{{ date }}の実績</h3>
            <div class="row mt-3" v-if="activityRes">
                <div class="col-4">
                    <div class="bg-white p-4 rounded shadow">
                        <h3 class="small">目標時間</h3>
                        <div class="d-flex align-items-baseline justify-content-center">
                            <span class="h3 fw-bold text-center" data-testid="show-target-time">{{ activityRes.data.target_time }}</span>
                            時間
                        </div>
                    </div>
                </div>
                <div class="col-4">
                    <div class="bg-white p-4 rounded shadow">
                        <h3 class="small">活動時間</h3>
                        <div class="d-flex align-items-baseline justify-content-center">
                            <span class="h3 fw-bold text-center" data-testid="show-actual-time">{{ activityRes.data.actual_time }}</span>
                            時間
                        </div>
                    </div>
                </div>
                <div class="col-4">
                    <div class="bg-white p-4 rounded shadow">
                        <h3 class="small">ステータス</h3>
                        <div class="d-flex align-items-baseline justify-content-center">
                            <span class="h3 fw-bold text-center" :class="getStatusColors[activityRes.data.status]"  data-testid="show-status">{{ STATUS_DICT[activityRes.data.status] }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div v-if="checkMsg" class="row d-flex justify-content-center mt-3">
                <p class="alert alert-warning" data-testid="checkMsg">{{ checkMsg }}</p>
            </div>
        </div>

        <div class="container d-flex align-items-baseline justify-content-center mt-4">
            <div class="row">
                <div class="input-group">
                    <span class="col-2 p-2 input-group-text">日付</span>
                    <input
                        type="date"
                        v-model="date"
                        min="2024-01-01"
                        :max="getMaxDate()"
                        class="form-control"
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
            </div>
        </div>

        <!-- タブによる画面切り替え -->
        <div class="container">
          <TargetTab
            v-if="activeTab === 'target'"
            @registered="renewActivities"
          />
          <ActualTab 
            v-else-if="activeTab === 'actual'"
            :pending-activities="pendingActivities"
            @registered="renewActivities"
          />
          <FinishTab
          v-else-if="activeTab === 'finish'"
            :pending-activities="pendingActivities"
            @registered="renewActivities"
          />
        </div>
        <br>
        <div class="container card">
            <h5 class="card-title mt-3 clickable" @click="isFormVisible = !isFormVisible">
                未確定の活動日
                <span v-if="isFormVisible" class="ms-2">▲</span>
                <span v-else class="ms-2">▼</span>
            </h5>
            <hr class="divider">
            <div class="collapse" :class="{ 'show': isFormVisible }">
                <div class="text-start mt-3" v-if="pendingActivities?.length > 0">
                    <table class="table table-striped table-responsive">
                    <thead class="table-dark">
                        <tr>
                        <th class="col-3">日付</th>
                        <th>目標時間</th>
                        <th>活動時間</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(activity, index) in pendingActivities" :key="index">
                        <td>{{ activity.date }}</td>
                        <td>{{ activity.target_time }}時間</td>
                        <td>{{ activity.actual_time }}時間</td>
                        </tr>
                    </tbody>
                    </table>
                </div>
                <div v-if="pendingMsg" class="alert" :class="getResponseAlert(pendingStatus)" data-testid="pendingMsg">
                    {{ pendingMsg }}
                </div>
            </div>
        </div>
        <br>
    </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { BButton, BCard, BCardText } from 'bootstrap-vue-next';
import { useRouter } from 'vue-router';
import TargetTab from './TargetTab.vue';
import ActualTab from './ActualTab.vue';
import FinishTab from './FinishTab.vue';
import { useFetchActivtiesByStatus, useFetchActivtyByDay } from './composables/useActivitesFetch';
import { useFetchMonthlySalary } from './composables/useSalary';
import { getResponseAlert, getStatusColors, STATUS_DICT } from './utils/ui';
import { changeDate, getThisMonth, getMaxDate } from './utils/date';

export default {
    components: {
        BButton,
        BCard,
        BCardText,
        TargetTab,
        ActualTab,
        FinishTab
    },

    setup() {
      const activeTab = ref("target");
      const tabs = [
        { value: 'target', label: '目標時間' },
        { value: 'actual', label: '活動時間' },
        { value: 'finish', label: '活動終了' }
      ];

      const router = useRouter();
      const isFormVisible = ref(false);
      const { date, checkMsg, activityRes, fetchActivityByDay } = useFetchActivtyByDay();
      const { increaseDay } = changeDate(date, checkMsg);
      const { pendingMsg, pendingActivities, pendingStatus, fetchActivitiesByStatus } = useFetchActivtiesByStatus();
      const { fetchMsg: incomeMsg, fetchRes: incomeRes, fetchMonthlySalary } = useFetchMonthlySalary();

      const renewActivities = async() => {
          await fetchActivityByDay();
          await fetchActivitiesByStatus("pending");
          checkMsg.value = "";
      };

      watch(date, () => {
          fetchActivityByDay();
      });

      onMounted( async() => {
        try {
          await fetchActivityByDay();
          await fetchActivitiesByStatus("pending");
          const thisMonth = getThisMonth();
          const dateParts = thisMonth.split("-");
          await fetchMonthlySalary(dateParts[0], dateParts[1]);
          if (incomeRes.value?.status!==404){
            router.push(
              {"path":"/register/salary",
                "query":{incomeMsg:`${incomeMsg.value}。先に月収を登録してください`}
              })
          };
        }
        catch (error){
          checkMsg.value = "ページ情報の取得に失敗しました";
        }
      });

    return {
        activeTab,
        tabs,
        date,
        checkMsg,
        activityRes,
        pendingActivities,
        pendingStatus,
        pendingMsg,
        increaseDay,
        STATUS_DICT,
        getMaxDate,
        getStatusColors,
        getResponseAlert,
        renewActivities,
        isFormVisible
      }
    }
}
</script>
