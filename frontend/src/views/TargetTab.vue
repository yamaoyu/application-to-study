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
          <td data-testid="target-row">
            <div class="input-group">
              <input 
                v-model="activity.date" 
                type="date" 
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
                v-model="activity.target_time"
                type="number"
                class="form-control text-center"
                min="0.5"
                max="12"
                step="0.5"
                :data-testid="`target-time-row-${index}`"
                @input="onValidate($event, activity.target_time)"
              />
              <span class="input-group-text small">時間</span>
            </div>
          </td>
          <td>
            <button 
              type="button" 
              class="btn btn-outline-danger btn-sm"
              :data-testid="`decrease-target-row-${index}`"
              @click="removeTargetActivity(targetActivities, index)"
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
              data-testid="increase-target-row"
              @click="addTargetActivity(targetActivities)"
            >
              + 行を追加
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <button 
      type="button" 
      :disabled="!isValid"
      data-testid="submit-multi-target"
      class="btn btn-outline-secondary mt-3"
      @click="showModal = true"
    >
      まとめて登録
    </button>
  </div>

  <div v-if="reqMsg" class="container d-flex justify-content-center" data-testid="reqMsg">
    <p class="mt-3 col-12" :class="getResponseAlert(statusCode)">{{ reqMsg }}</p>
  </div>

  <!-- モーダルコンポーネントで登録前の確認 -->
  <BModal v-model="showModal" title="目標時間の登録" ok-title="はい" cancel-title="いいえ" data-testid="modal-show" @ok="onSubmit">
    <p>入力した日の目標時間を登録しますか？</p>
  </BModal>
</template>

<script lang="ts">
import { ref, computed } from 'vue';
import { validateTargetTime, hasDuplicateDate, isValidActivities } from './utils/activity';
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
  
  setup(_props, { emit }) {
    const { targetActivities, reqMsg, statusCode, sendRequest } = useRegisterTargets();
    const date = ref<string>(getToday());
    const showModal = ref<boolean>(false);

    const onValidate = (event: Event, time: number) => {
      const input = event.target as HTMLInputElement;
      const error = validateTargetTime(time)

      if (error) {
        input.setCustomValidity(error)
        input.reportValidity()
      } else {
        input.setCustomValidity("")
      }
    };

    const checkDuplicateDate = (date: string, index: number) => {
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

