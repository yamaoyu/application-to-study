<template>
  <div>
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
                @input="onValidate($event, activity.target_time)"
                :data-testid="`target-time-row-${index}`"
              />
              <span class="input-group-text small">時間</span>
            </div>
          </td>
          <td>
            <button 
              type="button" 
              class="btn btn-outline-danger btn-sm"
              @click="removeTargetActivity(targetActivities, index)"
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
              @click="addTargetActivity(targetActivities)"
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
      @click="showModal = true"
      :disabled="!isValid"
      data-testid="submit-multi-target"
    >
      まとめて登録
    </button>
  </div>

  <div class="container d-flex justify-content-center" v-if="reqMsg" data-testid="reqMsg">
    <p class="mt-3 col-12" :class="getResponseAlert(statusCode)">{{ reqMsg }}</p>
  </div>

  <!-- モーダルコンポーネントで登録前の確認 -->
  <BModal v-model="showModal" title="目標時間の登録" ok-title="はい" cancel-title="いいえ" @ok="onSubmit" data-testid="modal-show">
    <p>入力した日の目標時間を登録しますか？</p>
  </BModal>
</template>

<script>
import { ref, computed } from 'vue';
import { validateTargetTime, hasDuplicateDate, isValidActivities } from './utils/activityValidation';
import { getMaxDate, getToday } from './utils/date';
import { useRegisterTargets, addTargetActivity, removeTargetActivity } from './composables/useTargetActivities';
import { BModal, BCard, BCardText } from 'bootstrap-vue-next';
import { getResponseAlert } from './utils/ui';

export default {
  components: {
    BModal,
    BCard,
    BCardText
  },

  emits: ['registered'],
  
  setup({}, { emit }) {
    const { targetActivities, reqMsg, statusCode, sendRequest } = useRegisterTargets();
    const date = ref(getToday());
    const showModal = ref(false);

    const onValidate = (event, time) => {
      const error = validateTargetTime(time)

      if (error) {
        event.target.setCustomValidity(error)
        event.target.reportValidity()
      } else {
        event.target.setCustomValidity("")
      }
    };

    const checkDuplicateDate = (date, index) => {
      if (hasDuplicateDate(targetActivities.value.map(a => a.date), date)) {
        targetActivities.value[index].date = "";
        reqMsg.value = `${date}は既に選択されています`;
      }
    };

    const isValid = computed(() => isValidActivities(targetActivities.value));

    const onSubmit = async () => {
      await sendRequest();
      emit('registered');
    };
    
    return {
      onValidate,
      checkDuplicateDate,
      targetActivities,
      reqMsg,
      statusCode,
      date,
      showModal,
      getMaxDate,
      addTargetActivity,
      removeTargetActivity,
      isValid,
      onSubmit,
      getResponseAlert
    }
  }
}
</script>

