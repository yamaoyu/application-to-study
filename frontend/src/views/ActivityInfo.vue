<template>
    <div class="d-flex mb-5 align-items-baseline justify-content-center">
        <BButton 
            v-for="tab in tabs" 
            :key="tab.value"
            @click="activeTab = tab.value"
            :variant="activeTab === tab.value ? 'primary' : 'outline-secondary'"
            class="me-2"
        >
            {{ tab.label }}
        </BButton>
    </div>

    <div>
        <div v-if="activeTab === 'monthly'">
            <div class="container col-8 d-flex justify-content-center">
                <div class="input-group">
                    <input
                    type="month"
                    v-model="selectedMonth"
                    :min="minMonth"
                    :max="maxMonth"
                    class="form-control col-2  border-secondary"
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
        </div>
        <div v-if="activeTab === 'yearly'">
            <div class="container col-8 d-flex justify-content-center">
                <div class="input-group">
                    <input
                    type="number"
                    v-model="selectedYear"
                    :min="minYear"
                    :max="maxYear"
                    class="form-control col-2 text-center border-secondary"
                    />
                </div>
            </div>
        </div>

        <div class="container mt-3" v-if="response">
            <div>
                <h2 v-if="activeTab==='monthly'">{{ selectedMonth }}の活動実績</h2>
                <h2 v-if="activeTab==='yearly'">{{ selectedYear }}の活動実績</h2>
                <h2 v-if="activeTab==='all'">全期間の集計</h2>
            </div>
            <div class="row justify-content-center mb-4">
                <div class="col-8">
                    <div class="bg-white p-4 rounded shadow">
                        <h3 class="small">合計</h3>
                        <div class="d-flex align-items-baseline justify-content-center">
                            <span :class="getAdjustmentColors(response)" class="h3 fw-bold text-center">{{ response.data.total_income }}</span>
                            万円
                        </div>
                    </div>
                </div>
                </div>
                <div class="row">
                <div class="col-6">
                    <div class="bg-white p-4 rounded shadow">
                        <h3 class="small">月収(ベース)</h3>
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
    </div>


    <div class="container mt-5">
        <div v-show="activeTab === 'monthly'">
            <div v-if="activities.length > 0" class="activities">
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
        </div>
        <div v-show="activeTab === 'yearly'">
            <div v-if="Object.keys(activities).length > 0" class="activities mt-5">
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
                    <td v-else>ー</td>
                    <td v-if="activity.bonus" class="fw-bold text-center text-success">{{ activity.bonus }}万円</td>
                    <td v-else>ー</td>
                    <td v-if="activity.penalty" class="fw-bold text-center text-danger">{{ activity.penalty }}万円</td>
                    <td v-else>ー</td>
                    <td v-if="activity.success_days" class="fw-bold text-center text-success">{{ activity.success_days }}日</td>
                    <td v-else>ー</td>
                    <td v-if="activity.fail_days" class="fw-bold text-center text-danger">{{ activity.fail_days }}日</td>
                    <td v-else>ー</td>
                    </tr>
                </tbody>
                </table>
            </div>
        </div>
        <!-- メッセージは全てのタブで共通 -->
        <div class="container d-flex justify-content-center">
            <p v-if="message" class="col-8 alert alert-warning">{{ message }}</p>
        </div>
    </div>


</template>

<script>
import { ref, watch, computed, onMounted } from 'vue';
import { debounce } from 'lodash'
import { BButton } from 'bootstrap-vue-next';
import { 
        getMaxMonth, getMaxYear, changeMonth, changeYear, 
        getAdjustmentColors, getStatusColors, STATUS_DICT, MONTH_DICT,
        getThisMonth, getThisYear, 
        getActivityByMonth, getActivityByYear, getActivitiesAllPeriod 
    } from './lib';


export default {
    components:{
        BButton
    },

    setup() {
        const activeTab = ref('monthly')
        const selectedMonth = ref(getThisMonth())
        const selectedYear = ref(getThisYear())
        const response = ref()
        const activities = ref([])
        const message = ref("")
        const minMonth = "2024-01";
        const maxMonth = getMaxMonth();
        const isAtMinMonth = computed(() => selectedMonth.value <= minMonth)
        const isAtMaxMonth = computed(() => selectedMonth.value >= maxMonth)
        const isAtMinYear = computed(() => selectedMonth.value <= "2024-12")
        const isAtMaxYear = computed(() => selectedMonth.value >= maxMonth.split("-")[0])
        const minYear = "2024";
        const maxYear = getMaxYear();
        const { increaseYear } = changeYear(selectedMonth);
        const { increaseMonth } = changeMonth(selectedMonth);
        const { getMonthlyInfo } = getActivityByMonth(selectedMonth, response, activities, message)
        const { getYearlyInfo } = getActivityByYear(selectedYear, response, activities, message)
        const { getAllActivities } = getActivitiesAllPeriod(response, message)
        const tabs = [
                    { value: 'monthly', label: '月別' },
                    { value: 'yearly', label: '年別' },
                    { value: 'all', label: '全期間' }
                    ]; 

        const debouncedRequest = debounce(() => {
            if (activeTab.value==='monthly'){
                getMonthlyInfo();
                activities.value = []
                response.value = ""
            } else if(activeTab.value==='yearly'){
                getYearlyInfo();
                activities.value = []
                response.value = ""
            }
        }, 500);

        watch(activeTab, () => {
            activities.value = []
            response.value = ""
            if (activeTab.value==="all"){
                getAllActivities()
            } else if (activeTab.value==='monthly'){
                getMonthlyInfo();
            } else if(activeTab.value==='yearly'){
                getYearlyInfo();
            }
        })

        watch(selectedYear, () => {
            debouncedRequest()
        })

        watch(selectedMonth, () =>{
            debouncedRequest()
        })

        onMounted(()=>{
            getMonthlyInfo()
        })


    return {
        activeTab,
        tabs,
        selectedMonth,
        selectedYear,
        response,
        activities,
        message,
        minMonth,
        maxMonth,
        isAtMinMonth,
        isAtMaxMonth,
        isAtMinYear,
        isAtMaxYear,
        minYear,
        maxYear,
        getAdjustmentColors,
        getStatusColors,
        STATUS_DICT,
        MONTH_DICT,
        increaseYear,
        increaseMonth,
        getMonthlyInfo,
        getYearlyInfo,
        getAllActivities
    }

    },
}

</script>