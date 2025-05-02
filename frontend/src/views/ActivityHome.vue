<template>
    <div class="container">
        <div class="d-flex mb-3 align-items-baseline justify-content-center">
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

        <div class="container">
            <h3 class="mt-5">{{ date }}の実績</h3>
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

        <div class="container d-flex align-items-baseline justify-content-center mt-5">
            <div class="row col-8">
                <div class="input-group">
                    <span class="col-2 p-2 input-group-text">日付</span>
                    <input
                        type="date"
                        v-model="date"
                        min="2024-01-01"
                        :max="getMaxDate()"
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
            </div>
        </div>

        <!-- タブによる画面切り替え -->
        <div class="container col-8">
            <div v-show="activeTab === 'target'">
                <form @submit.prevent="confirmRegister">
                    <div class="row d-flex justify-content-center mt-4">
                        <div class="input-group">
                            <span class="input-group-text">目標時間</span>
                                <input
                                type="number"
                                v-model="targetTime"
                                class="form-control col-2 text-center"
                                min="0.5"
                                max="12"
                                step="0.5"
                                />
                            <span class="input-group-text small">時間(Hour)</span>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-outline-secondary mt-3">登録</button>
                </form>
            </div>
            <div v-show="activeTab === 'actual'">
                <form @submit.prevent="confirmRegister">
                    <div class="row d-flex justify-content-center mt-4">
                        <div class="input-group">
                            <span class="input-group-text">活動時間</span>
                                <input
                                type="number"
                                v-model="actualTime"
                                class="form-control col-2 text-center"
                                min="0.0"
                                max="12"
                                step="0.5"
                                />
                            <span class="input-group-text small">時間(Hour)</span>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-outline-secondary mt-3">登録</button>
                </form>
            </div>
            <div v-show="activeTab === 'finish'">
                <form @submit.prevent="confirmRegister">
                    <div class="container">
                        <button type="submit" class="btn btn-outline-secondary mt-3">終了</button>
                    </div>
                </form>
            </div>
            <div class="container d-flex justify-content-center">
                <p v-if="message" class="mt-3 col-12" :class="getResponseAlert(statusCode)">{{ message }}</p>
                <p v-if="finMsg" class="mt-3 col-12" :class="getActivityAlert(activityStatus)">{{ finMsg }}</p>
            </div>
        </div>
        <br>
        <div class="container card">
            <h5 class="card-title mt-3 clickable" @click="toggleFormVisibility">未確定の活動日</h5>
            <hr class="divider">
            <div class="collapse" :class="{ 'show': isFormVisible }">
                <div class="text-start mt-3" v-if="Object.keys(pendingActivities).length > 0">
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
                <div v-if="pendingMsg" class="alert alert-success">
                    {{ pendingMsg }}
                </div>
            </div>
        </div>
        <br>
    </div>

    <!-- モーダルコンポーネントで登録前の確認 -->
    <BModal v-model="showModal" :title="modalTitle" ok-title="はい" cancel-title="いいえ" @ok="sendRequest">
        <p>{{ modalMessage }}</p>
        <p v-if="activeTab==='finish'" class="text-danger">確定後は取り消せません</p>
    </BModal>

</template>

<script>
import { ref, watch, onMounted, computed } from 'vue';
import { BButton, BModal } from 'bootstrap-vue-next';
import { 
    changeDate, STATUS_DICT, getStatusColors, getToday, getMaxDate,
    getActivityAlert, getResponseAlert, updateActivity, registerActivity, 
    finalizeActivity, getActivitiesByStatus } from './lib/index';

export default {
    components: {
        BButton,
        BModal
    },

    setup() {
        const activeTab = ref("target");
        const date = ref(getToday());
        const statusCode = ref();
        const targetTime = ref(0.5);
        const actualTime = ref(0);
        const message = ref("");
        const checkMsg = ref("");
        const finMsg = ref("");
        const activityRes = ref("");
        const activityStatus = ref("");
        const isFormVisible = ref(false)
        const pendingActivities = ref([]);
        const pendingMsg = ref("")
        const tabs = [
                    { value: 'target', label: '目標時間' },
                    { value: 'actual', label: '活動時間' },
                    { value: 'finish', label: '活動終了' }
                    ];
        const { increaseDay } = changeDate(date, message);
        const { renewActivity } = updateActivity(date, checkMsg, activityRes);
        const { registerTarget, registerActual } = registerActivity(date, statusCode, targetTime, actualTime, message, checkMsg, activityRes);
        const { finishActivity } = finalizeActivity(date, finMsg, activityStatus, checkMsg, activityRes);
        const { getPendingActivities } = getActivitiesByStatus(pendingActivities, pendingMsg)
        const showModal = ref(false);

        const toggleFormVisibility = () => {
            isFormVisible.value = !isFormVisible.value
        }

        const confirmRegister = async() =>{
            showModal.value = true
        }

        const modalTitle = computed(() =>{
            if (showModal.value) {
                switch(activeTab.value) {
                    case 'target': return '目標時間の登録';
                    case 'actual': return '活動時間の登録';
                    case 'finish': return '活動時間の確定';
                }
            }
            return ''
        });

        const modalMessage = computed(() =>{
            if (showModal.value) {
                switch(activeTab.value) {
                    case 'target': return `${date.value}の目標時間を ${targetTime.value}時間に登録しますか？`;
                    case 'actual': return `${date.value}の活動時間を ${actualTime.value}時間に登録しますか？`;
                    case 'finish': return `${date.value}の活動を終了しますか？`;
                }
            }
            return ''
        });

        const sendRequest = async() =>{
            if (showModal.value) {
                switch(activeTab.value) {
                    case 'target':
                    await registerTarget();
                    await getPendingActivities();
                    break;
                case 'actual':
                    await registerActual();
                    await getPendingActivities();
                    break;
                case 'finish':
                    await finishActivity();
                    await getPendingActivities();
                    break;
                }
            }
        }

        watch(date, () => {
            renewActivity();
            message.value = "";
            finMsg.value = "";
        });

        watch(activeTab, () => {
            message.value = "";
            finMsg.value = "";
        }
    )

        onMounted(() => {
            renewActivity();
            getPendingActivities();
        });

    return {
            activeTab,
            tabs,
            date,
            statusCode,
            targetTime,
            actualTime,
            message,
            checkMsg,
            finMsg,
            activityRes,
            activityStatus,
            pendingActivities,
            getPendingActivities,
            pendingMsg,
            increaseDay,
            STATUS_DICT,
            getMaxDate,
            getStatusColors,
            getActivityAlert,
            getResponseAlert,
            renewActivity,
            registerTarget,
            registerActual,
            finishActivity,
            showModal,
            confirmRegister,
            toggleFormVisibility,
            isFormVisible,
            modalTitle,
            modalMessage,
            sendRequest
        }
    }
}
</script>