<template>
    <div class="container">
        <div class="d-flex mb-3 align-items-baseline justify-content-center">
            <BButton 
                v-for="type in types" 
                :key="type.value"
                @click="registertype = type.value"
                :variant="registertype === type.value ? 'primary' : 'outline-secondary'"
                class="me-2"
            >
                {{ type.label }}
            </BButton>
        </div>
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
                <p class="alert alert-warning">{{ checkMsg }}</p>
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
            <div v-show="activeTab === 'target' && registertype === 'single'">
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
            <div v-show="activeTab === 'actual' && registertype === 'single'">
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
            <div v-show="activeTab === 'finish' && registertype === 'single'">
                <form @submit.prevent="confirmRegister">
                    <div class="container">
                        <button type="submit" class="btn btn-outline-secondary mt-3">終了</button>
                    </div>
                </form>
            </div>
            <div v-show="activeTab === 'target' && registertype === 'multi'">
                <BCard class="border-0 shadow-sm mt-3" bg-variant="light">
                    <div class="text-center">
                        <h5 class="card-title text-primary fw-bold mb-2">
                            <i class="bi bi-target me-2"></i>目標時間の設定
                        </h5>
                        <BCardText class="text-muted small mb-0">
                            日付を選択し、目標時間を入力してください
                        </BCardText>
                    </div>
                </BCard>
                <table class="table table-striped table-responsive">
                    <thead class="table-dark">
                        <tr>
                            <th class="col-2">日付</th>
                            <th class="col-2">目標時間</th>
                            <th class="col-1"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(activity, index) in targetActivities" :key="index">
                            <td>
                                <div class="input-group">
                                    <input type="date" v-model="activity.date" class="form-control" />
                                </div>
                            </td>
                            <td>
                                <div class="input-group">
                                    <input
                                        type="number"
                                        v-model="activity.target_time"
                                        class="form-control text-center"
                                        min="0.5"
                                        max="12"
                                        step="0.5"
                                        placeholder="0.5"
                                    />
                                    <span class="input-group-text small">時間</span>
                                </div>
                            </td>
                            <td>
                                <button 
                                    type="button" 
                                    class="btn btn-outline-danger btn-sm"
                                    @click="removeTargetActivity(index)"
                                >
                                    削除
                                </button>
                            </td>
                        </tr>
                        <tr class="table-secondary">
                            <td colspan="3" class="text-center">
                                <button 
                                    type="button" 
                                    class="btn btn-outline-primary"
                                    @click="addTargetActivity"
                                >
                                    + 行を追加
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <button 
                    type="button" 
                    class="btn btn-outline-secondary mt-3"
                    @click="confirmRegister"
                    :disabled="!isValidActivities"
                >
                    まとめて登録
                </button>
            </div>
            <div v-show="activeTab === 'actual' && registertype === 'multi'">
                <div v-if="Object.keys(pendingActivities).length > 0" class="mt-3">
                    <BCard class="border-0 shadow-sm mt-3" bg-variant="light">
                        <div class="text-center">
                            <h5 class="card-title text-primary fw-bold mb-2">
                                <i class="bi bi-target me-2"></i>活動時間の設定
                            </h5>
                            <BCardText class="text-muted small mb-0">
                                日付を選択し、活動時間を入力してください
                            </BCardText>
                        </div>
                    </BCard>
                    <table class="table table-striped table-responsive">
                        <thead class="table-dark">
                            <tr>
                                <th class="col-1"></th>
                                <th class="col-2">日付</th>
                                <th class="col-2">目標時間</th>
                                <th class="col-2">活動時間</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(activity, index) in pendingActivities" 
                                :key="index" 
                                @click="toggleActivity(activity)"
                                :class="{ 'table-active': isSelected(activity) }"
                                style="cursor: pointer;"
                            >
                                <td>
                                    <input 
                                        class="form-check-input" 
                                        type="checkbox"
                                        :value="activity"
                                        v-model="selectedActivities"
                                    >
                                </td>
                                <td>{{ activity.date }}</td>
                                <td>{{ activity.target_time }}時間</td>
                                <td>
                                <div class="input-group">
                                    <input
                                        type="number"
                                        v-model="activity.actual_time"
                                        class="form-control text-center"
                                        min="0.0"
                                        max="12"
                                        step="0.5"
                                        placeholder="0.0"
                                    />
                                    <span class="input-group-text small">時間</span>
                                </div>
                            </td>
                            </tr>
                        </tbody>
                    </table>
                    <button 
                        type="button" 
                        class="btn btn-outline-secondary mt-3"
                        @click="confirmRegister"
                        :disabled="selectedActivities.length === 0"
                    >
                        まとめて登録
                    </button>
                </div>
            </div>
            <div v-show="activeTab === 'finish' && registertype === 'multi'">
                <div v-if="Object.keys(pendingActivities).length > 0" class="mt-3">
                    <BCard class="border-0 shadow-sm mt-3" bg-variant="light">
                        <div class="text-center">
                            <h5 class="card-title text-primary fw-bold mb-2">
                                <i class="bi bi-target me-2"></i>活動の終了
                            </h5>
                            <BCardText class="text-muted small mb-0">
                                活動を終了する日を選択してください
                            </BCardText>
                        </div>
                    </BCard>
                    <table class="table table-striped table-responsive">
                        <thead class="table-dark">
                            <tr>
                                <th class="col-1"></th>
                                <th class="col-2">日付</th>
                                <th class="col-2">目標時間</th>
                                <th class="col-2">活動時間</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(activity, index) in pendingActivities" 
                                :key="index" 
                                @click="toggleActivity(activity.date)"
                                :class="{ 'table-active': isSelected(activity.date) }"
                                style="cursor: pointer;"
                            >
                                <td>
                                    <input 
                                        class="form-check-input" 
                                        type="checkbox"
                                        :value="activity.date"
                                        v-model="selectedActivities"
                                    >
                                </td>
                                <td>{{ activity.date }}</td>
                                <td>{{ activity.target_time }}時間</td>
                                <td>{{ activity.actual_time }}時間</td>
                            </tr>
                        </tbody>
                    </table>
                    <button 
                        type="button" 
                        class="btn btn-outline-secondary mt-3"
                        @click="confirmRegister"
                        :disabled="selectedActivities.length === 0"
                    >
                        まとめて終了
                    </button>
                </div>
                <div v-else class="mt-3">
                    <p class="text-muted">確定可能な活動がありません</p>
                </div>
            </div>
            <div class="container d-flex justify-content-center">
                <p v-if="reqMsg" class="mt-3 col-12" :class="getResponseAlert(statusCode)">{{ reqMsg }}</p>
            </div>
        </div>
        <br>
        <div class="container card">
            <h5 class="card-title mt-3 clickable" @click="toggleFormVisibility">
                未確定の活動日
                <span v-if="isFormVisible" class="ms-2">▲</span>
                <span v-else class="ms-2">▼</span>
            </h5>
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
import { BButton, BModal, BCard, BCardText } from 'bootstrap-vue-next';
import { 
    changeDate, STATUS_DICT, getStatusColors, getToday, getMaxDate,
    getResponseAlert, updateActivity, registerTarget, registerActual, 
    finalizeActivity,finalizeMultiActivities, getActivitiesByStatus, 
    registerMultiTarget, registerMultiActual} from './lib/index';

export default {
    components: {
        BButton,
        BModal,
        BCard,
        BCardText
    },

    setup() {
        const activeTab = ref("target");
        const registertype = ref("single");
        const selectedActivities = ref([]);
        const targetActivities = ref([{ date: '', target_time: 0.5 }]);
        const date = ref(getToday());
        const statusCode = ref();
        const targetTime = ref(0.5);
        const actualTime = ref(0);
        const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
        const checkMsg = ref(""); // 活動の詳細を確認するためのメッセージ
        const activityRes = ref("");
        const isFormVisible = ref(false)
        const pendingActivities = ref([]);
        const pendingMsg = ref("")
        const tabs = [
                    { value: 'target', label: '目標時間' },
                    { value: 'actual', label: '活動時間' },
                    { value: 'finish', label: '活動終了' }
                    ];
        const types = [
                    { value: 'single', label: '個別' },
                    { value: 'multi', label: '一括' }
                    ];
        const MultiActivities = ref();
        const { increaseDay } = changeDate(date, reqMsg);
        const { renewActivity } = updateActivity(date, checkMsg, activityRes);
        const { register: submitTarget } = registerTarget(date, statusCode, targetTime, reqMsg, checkMsg, activityRes);
        const { register: submitActual } = registerActual(date, statusCode, actualTime, reqMsg, checkMsg, activityRes);
        const { register: submitMultiTarget } = registerMultiTarget(date, statusCode, reqMsg, targetActivities, checkMsg, activityRes);
        const { register: submitMultiActual } = registerMultiActual(date, statusCode, reqMsg, selectedActivities, checkMsg, activityRes);
        const { finishActivity } = finalizeActivity(date, reqMsg, statusCode, checkMsg, activityRes);
        const { finishMultiActivities } = finalizeMultiActivities(date, selectedActivities, reqMsg, statusCode, checkMsg, activityRes);
        const { getPendingActivities } = getActivitiesByStatus(pendingActivities, pendingMsg)
        const showModal = ref(false);

        const toggleFormVisibility = () => {
            isFormVisible.value = !isFormVisible.value
        }

        const toggleActivity = (activity) => {
            if (isSelected(activity)) {
                selectedActivities.value.splice(selectedActivities.value.indexOf(activity), 1);
            } else {
                selectedActivities.value.push(activity)
            }
        }

        const isSelected = (activity) => {
            return selectedActivities.value.includes(activity);
        };

        const confirmRegister = async() =>{
            showModal.value = true
        }

        const addTargetActivity = () => {
            targetActivities.value.push({ date: '', target_time: 0.5 });
        };

        const removeTargetActivity = (index) => {
            if (targetActivities.value.length > 1) {
                targetActivities.value.splice(index, 1);
            } else {
                targetActivities.value[0].target_time = 0.5;
                targetActivities.value[0].date = "";
            }
        };

        const isValidActivities = computed(() => {
            // 目標時間送信用の変数(targetActivities)で日付と目標時間が入力されているか確認
            if (targetActivities.value.some(activity => !activity.date || !activity.target_time)) {
                return false
            } else {
                return true
            }
        });

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
                switch(registertype.value){
                    case 'single':
                        switch(activeTab.value) {
                            case 'target': return `${date.value}の目標時間を ${targetTime.value}時間に登録しますか？`;
                            case 'actual': return `${date.value}の活動時間を ${actualTime.value}時間に登録しますか？`;
                            case 'finish': return `${date.value}の活動を終了しますか？`;
                        }
                        break;
                    case 'multi':
                        switch(activeTab.value) {
                            case 'target': return `入力した日の目標時間を登録しますか？`;
                            case 'actual': return `選択した日の活動時間を登録しますか？`;
                            case 'finish': return `選択した日の活動を終了しますか？`
                        }
                        break;
                }
            }
            return ''
        })

        const sendRequest = async() =>{
            if (showModal.value) {
                if (registertype.value === 'single') {
                    switch(activeTab.value) {
                        case 'target':
                            await submitTarget();
                            await getPendingActivities();
                            break;
                        case 'actual':
                            await submitActual();
                            await getPendingActivities();
                            break;
                        case 'finish':
                            await finishActivity();
                            await getPendingActivities();
                            break;
                    }
                } else if (registertype.value === 'multi') {
                    switch(activeTab.value) {
                        case 'target':
                            await submitMultiTarget();
                            await getPendingActivities();
                            break;
                        case 'actual':
                            await submitMultiActual();
                            await getPendingActivities();
                            break;
                        case 'finish':
                            await finishMultiActivities();
                            await getPendingActivities();
                            break;
                    }
                }
            }
        }

        watch(date, () => {
            renewActivity();
            reqMsg.value = "";
        });

        watch(activeTab, () => {
            reqMsg.value = "";
            selectedActivities.value = [];
        })

        watch(registertype, () => {
            reqMsg.value = "";
        })

        onMounted(() => {
            renewActivity();
            getPendingActivities();
        });

    return {
            activeTab,
            registertype,
            tabs,
            types,
            selectedActivities,
            targetActivities,
            MultiActivities,
            date,
            statusCode,
            targetTime,
            actualTime,
            reqMsg,
            checkMsg,
            activityRes,
            pendingActivities,
            getPendingActivities,
            pendingMsg,
            increaseDay,
            STATUS_DICT,
            getMaxDate,
            getStatusColors,
            getResponseAlert,
            renewActivity,
            showModal,
            confirmRegister,
            addTargetActivity,
            isValidActivities,
            isSelected,
            removeTargetActivity,
            toggleActivity,
            toggleFormVisibility,
            isFormVisible,
            modalTitle,
            modalMessage,
            sendRequest
        }
    }
}
</script>