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
            <div v-show="activeTab === 'target'">
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
                                    <input 
                                        type="date" 
                                        v-model="activity.date" 
                                        class="form-control" 
                                        min="2024-01-01"
                                        :max="getMaxDate()"
                                        :data-testid="`target-date-row-${index}`"
                                        @change="checkDuplicateDate(activity.date, index)"
                                    />
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
                                        @input="validateTime($event, activity.target_time)"
                                        :data-testid="`target-time-row-${index}`"
                                    />
                                    <span class="input-group-text small">時間</span>
                                </div>
                            </td>
                            <td>
                                <button 
                                    type="button" 
                                    class="btn btn-outline-danger btn-sm"
                                    @click="removeTargetActivity(index)"
                                    :data-testid="`decrease-target-row-${index}`"
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
                                    data-testid="increase-target-row"
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
                    data-testid="submit-multi-target"
                >
                    まとめて登録
                </button>
            </div>
            <div v-show="activeTab === 'actual'">
                <div v-if="Object.keys(editActivities).length > 0" class="mt-3">
                    <BCard class="border-0 shadow-sm mt-3" bg-variant="light">
                        <div class="text-center">
                            <h5 class="card-title text-primary fw-bold mb-2">
                                <i class="bi bi-target me-2"></i>活動時間の設定
                            </h5>
                            <BCardText class="text-muted small mb-0">
                                日付を選択し、活動時間を入力してください
                            </BCardText>
                        </div>
                        <button 
                            type="button" 
                            class="btn btn-primary btn-sm position-absolute"
                            style="top: 1rem; right: 1rem;"
                            data-testid="toggle-all-activities"
                            @click="toggleAllActivities"
                        >
                            {{ Object.keys(editActivities).length===Object.keys(selectedActivities).length ? '全て解除' : '全て選択' }}
                        </button>
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
                            <tr v-for="(activity, index) in editActivities" 
                                :key="index"
                                :class="{ 'table-active': isSelected(activity) }"
                            >
                                <td @click="toggleActivity(activity)" :data-testid="`is-selected-actual-${index}`">
                                    <input 
                                        class="form-check-input" 
                                        type="checkbox"
                                        :value="activity"
                                        v-model="selectedActivities"
                                    >
                                </td>
                                <td @click="toggleActivity(activity)">{{ activity.date }}</td>
                                <td @click="toggleActivity(activity)">{{ activity.target_time }}時間</td>
                                <td>
                                    <div class="input-group">
                                        <input
                                            type="number"
                                            v-model="activity.actual_time"
                                            class="form-control text-center"
                                            min="0.0"
                                            max="12"
                                            step="0.5"
                                            @input="validateTime($event, activity.actual_time)"
                                            :data-testid="`actual-time-row-${index}`"
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
                        data-testid="submit-multi-actual"
                    >
                        まとめて登録
                    </button>
                </div>
                <div v-else class="mt-3 alert alert-warning">登録対象の活動がありません</div>
            </div>
            <div v-show="activeTab === 'finish'">
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
                        <button 
                            type="button" 
                            class="btn btn-primary btn-sm position-absolute"
                            style="top: 1rem; right: 1rem;"
                            data-testid="toggle-all-activities"
                            @click="toggleAllActivities"
                        >
                            {{ Object.keys(pendingActivities).length===Object.keys(selectedActivities).length ? '全て解除' : '全て選択' }}
                        </button>
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
                            >
                                <td :data-testid="`is-selected-finish-${index}`">
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
                        data-testid="finish-multi"
                    >
                        まとめて終了
                    </button>
                </div>
                <div v-else class="mt-3 alert alert-warning">確定可能な活動がありません</div>
            </div>
            <div class="container d-flex justify-content-center" v-if="reqMsg" data-testid="reqMsg">
                <p v-if="activeTab==='finish'" class="mt-3 col-12" :class="getActivityAlert(activityStatus)">{{ reqMsg }}</p>
                <p v-else class="mt-3 col-12" :class="getResponseAlert(statusCode)">{{ reqMsg }}</p>
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
    <BModal v-model="showModal" :title="modalTitle" ok-title="はい" cancel-title="いいえ" @ok="sendRequest" data-testid="modal-show">
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
    registerMultiTarget, registerMultiActual, getActivityAlert} from './lib/index';

export default {
    components: {
        BButton,
        BModal,
        BCard,
        BCardText
    },

    setup() {
        const activeTab = ref("target");
        const selectedActivities = ref([]);
        const targetActivities = ref([{ date: '', target_time: 0.5 }]);
        const date = ref(getToday());
        const statusCode = ref();
        const activityStatus = ref();
        const targetTime = ref(0.5);
        const actualTime = ref(0);
        const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
        const checkMsg = ref(""); // 活動の詳細を確認するためのメッセージ
        const activityRes = ref("");
        const isFormVisible = ref(false)
        const pendingActivities = ref([]); // 未完了のアクティビティを表示する用
        const editActivities = ref([]); //未完了のアクティビティを編集するときに使用(pendingActivitiesに影響を及ぼさないため)
        const pendingMsg = ref("")
        const tabs = [
                    { value: 'target', label: '目標時間' },
                    { value: 'actual', label: '活動時間' },
                    { value: 'finish', label: '活動終了' }
                    ];
        const MultiActivities = ref();
        const { increaseDay } = changeDate(date, reqMsg);
        const { renewActivity } = updateActivity(date, checkMsg, activityRes);
        const { register: submitTarget } = registerTarget(date, statusCode, targetTime, reqMsg, checkMsg, activityRes);
        const { register: submitActual } = registerActual(date, statusCode, actualTime, reqMsg, checkMsg, activityRes);
        const { register: submitMultiTarget } = registerMultiTarget(date, statusCode, reqMsg, targetActivities, checkMsg, activityRes);
        const { register: submitMultiActual } = registerMultiActual(date, statusCode, reqMsg, selectedActivities, checkMsg, activityRes);
        const { finishActivity } = finalizeActivity(date, reqMsg, activityStatus, checkMsg, activityRes);
        const { finishMultiActivities } = finalizeMultiActivities(date, selectedActivities, reqMsg, statusCode, checkMsg, activityRes);
        const { getPendingActivities } = getActivitiesByStatus(pendingActivities, pendingMsg);
        const showModal = ref(false);

        const toggleFormVisibility = () => {
            isFormVisible.value = !isFormVisible.value;
        }

        const toggleActivity = (activity) => {
            if (isSelected(activity)) {
                selectedActivities.value.splice(selectedActivities.value.indexOf(activity), 1);
            } else {
                selectedActivities.value.push(activity);
            }
        }

        const isSelected = (activity) => {
            return selectedActivities.value.includes(activity);
        };

        const confirmRegister = async() =>{
            showModal.value = true;
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

        const toggleAllActivities = () => {
            if (activeTab.value === "actual") {
                if (editActivities.value.length===selectedActivities.value.length) {
                    selectedActivities.value.splice(0, selectedActivities.value.length);
                } else {
                    selectedActivities.value.splice(0, selectedActivities.value.length, ...editActivities.value);
                }
            } else {
                if (pendingActivities.value.length===selectedActivities.value.length) {
                    selectedActivities.value.splice(0, selectedActivities.value.length);
                } else {
                    selectedActivities.value.splice(0, selectedActivities.value.length, 
                            ...pendingActivities.value.map(activity => activity.date));
                }
            }
        };

        const validateTime = (event, time) =>{
            if (activeTab.value == "target" && time < 0.5) {
                // 時間が0.5時間未満の場合のエラーメッセージ
                event.target.setCustomValidity("時間は0.5時間以上入力してください");
                event.target.reportValidity();

            } else if (typeof(time) != 'number') {
                // 時間が入力されていない場合のエラーメッセージ
                event.target.setCustomValidity("時間を入力してください");
                event.target.reportValidity();
            } else if (time * 2 % 1 != 0){
                // 時間が0.5時間単位でない場合のエラーメッセージ
                event.target.setCustomValidity("時間は0.5時間単位で入力してください");
                event.target.reportValidity();
            } else {
                event.target.setCustomValidity("");
            }
        };

        const checkDuplicateDate = (date, index) => {
            const duplicateDate = targetActivities.value.map(a=>a.date).filter(d=>d && d===date);
            reqMsg.value = "";
            if (duplicateDate.length > 1) {
                targetActivities.value[index].date = "";
                reqMsg.value = date + "は既に選択されています"
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
                switch(activeTab.value) {
                    case 'target': return `入力した日の目標時間を登録しますか？`;
                    case 'actual': return `選択した日の活動時間を登録しますか？`;
                    case 'finish': return `選択した日の活動を終了しますか？`
                }
            }
            return ''
        })

        const sendRequest = async() =>{
            try {
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
            } finally {
                showModal.value = false;
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

        watch(pendingActivities, () => {
            editActivities.value = pendingActivities.value.map(activity =>({
                ...activity})
            )}, { 
                immediate: true,  // 初回実行
            }
        );

        onMounted(() => {
            renewActivity();
            getPendingActivities();
        });

    return {
            activeTab,
            tabs,
            selectedActivities,
            targetActivities,
            MultiActivities,
            date,
            statusCode,
            activityStatus,
            targetTime,
            actualTime,
            reqMsg,
            checkMsg,
            activityRes,
            pendingActivities,
            editActivities,
            pendingMsg,
            increaseDay,
            renewActivity,
            STATUS_DICT,
            getMaxDate,
            getStatusColors,
            getActivityAlert,
            getResponseAlert,
            showModal,
            confirmRegister,
            addTargetActivity,
            isValidActivities,
            isSelected,
            removeTargetActivity,
            toggleAllActivities,
            validateTime,
            checkDuplicateDate,
            toggleActivity,
            toggleFormVisibility,
            isFormVisible,
            modalTitle,
            modalMessage,
            sendRequest,
            submitTarget,
            submitActual,
            finishActivity,
            submitMultiTarget,
            submitMultiActual,
            finishMultiActivities
        }
    }
}
</script>