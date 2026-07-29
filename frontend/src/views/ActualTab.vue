<template>
  <div>
    <div v-if="Object.keys(editableActivities).length > 0" class="mt-3">
      <BCard class="border-0 shadow-sm mt-3" bg-variant="light">
        <div class="text-center">
          <h5 class="card-title text-primary fw-bold mb-2">
            <i class="bi bi-target me-2"></i>活動時間の設定
          </h5>
          <BCardText class="text-muted small mb-0">
            日付を選択し、活動時間を入力してください
          </BCardText>
        </div>
        <div class="mt-3 pt-3 border-top">
          <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
            <div class="d-flex flex-wrap gap-2">
              <button
                type="button"
                :disabled="editedActivities.length === 0"
                class="btn btn-primary btn-sm"
                data-testid="select-edited-activities"
                @click="applySelection('edited')"
              >
                変更分を選択({{ editedActivities.length }}件)
              </button>
              <button
                type="button"
                :disabled="editableActivities.length === 0"
                class="btn btn-outline-primary btn-sm"
                data-testid="select-all-activities"
                @click="applySelection('all')"
              >
                全て選択({{ editableActivities.length }}件)
              </button>
              <button
                type="button"
                :disabled="selectedActivities.length === 0"
                class="btn btn-outline-secondary btn-sm"
                data-testid="reset-selected-activities"
                @click="clear"
              >
                選択解除
              </button>
            </div>
            <div class="text-md-end">
              <div class="small text-muted">
                変更済み {{ editedActivities.length }}件
              </div>
              <button
                type="button"
                :disabled="editedActivities.length === 0"
                class="btn btn-outline-danger btn-sm mt-1"
                data-testid="reset-edited-activities"
                @click="resetEditedActivities"
              >
                変更を元に戻す
              </button>
            </div>
          </div>
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
          <tr 
            v-for="(activity, index) in editableActivities" 
            :key="index"
            :class="{ 'table-active': isSelected(activity), 'table-warning': isEditedActual(activity) }"
          >
            <td 
              :data-testid="`is-selected-actual-${index}`"
              @click="toggle(activity)" 
            >
                <input 
                    v-model="selectedActivities"
                    class="form-check-input" 
                    type="checkbox"
                    :value="activity"
                >
            </td>
            <td @click="toggle(activity)">{{ activity.date }}</td>
            <td @click="toggle(activity)">{{ activity.target_time }}時間</td>
            <td>
              <div class="input-group" data-testid="actual-row">
                <input
                  v-model="activity.actual_time"
                  :data-testid="`actual-time-row-${index}`"
                  type="number"
                  class="form-control text-center"
                  min="0.0"
                  max="12"
                  step="0.5"
                  @input="onValidate($event, activity.actual_time)"
                  
                />
                <span class="input-group-text small">時間</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
        <button 
          type="button" 
          :disabled="selectedActivities.length === 0"
          data-testid="submit-multi-actual"
          class="btn btn-outline-secondary mt-3"
          @click="showModal = true"
        >
          まとめて登録
        </button>
      </div>
    <div v-else class="mt-3 alert alert-warning">登録対象の活動がありません</div>
  </div>

  <div v-if="reqMsg" class="container d-flex justify-content-center" data-testid="reqMsg">
    <p class="mt-3 col-12" :class="getResponseAlert(statusCode)">{{ reqMsg }}</p>
  </div>

  <!-- モーダルコンポーネントで登録前の確認 -->
  <BModal 
    v-model="showModal"
    title="活動時間の登録" 
    ok-title="はい" 
    cancel-title="いいえ" 
    data-testid="modal-show"
    @ok="onSubmit" 
  >
    <p>選択した日の活動時間を登録しますか？</p>
  </BModal>
</template>

<script lang="ts">
import { ref, computed, watch, type PropType } from 'vue';
import { validateActualTime } from './utils/activityValidation';
import { useRegisterActuals } from './composables/useActualActivities';
import { getMaxDate, getToday } from './utils/date';
import { BModal, BCard, BCardText } from 'bootstrap-vue-next';
import { getResponseAlert } from './utils/ui';
import { useSelection } from './composables/useSelection';
import { OneActivity } from './types/activity';

type Mode = "all"| "edited"

export default {
  components: {
    BModal,
    BCard,
    BCardText
  },

  props: {
    pendingActivities: {
      type: Array as PropType<OneActivity[]>,
      default: () => []
    }
  },

  emits: ['registered'],

  setup(props, { emit }) {
    const date = ref<string>(getToday());
    const showModal = ref<boolean>(false);
    const editableActivities = ref<OneActivity[]>([]);
    const { selectedActivities, reqMsg, statusCode, sendRequest } = useRegisterActuals();
    const { isSelected, toggle, clear } = useSelection(selectedActivities);

    const onValidate = (event: Event, time:number) => {
      const input = event.target as HTMLInputElement;
      const error = validateActualTime(time)

      if (error) {
        input.setCustomValidity(error)
        input.reportValidity()
      } else {
        input.setCustomValidity("")
      }
    };

    const editedActivities = computed(() => {
      return editableActivities.value.filter(activity => isEditedActual(activity));
    });

    const pendingById = computed(() => {
      return new Map(props.pendingActivities.map(a => [a.activity_id, a]));
    });

    const isEditedActual = (activity: OneActivity) => {
      const originalActivity = pendingById.value.get(activity.activity_id);
      if (originalActivity) {
        return activity.actual_time !== originalActivity.actual_time;
      };
      return false;
    };


    const applySelection = (mode: Mode) => {
      if (mode === "all") {
        selectedActivities.value = [...editableActivities.value];
      } else if (mode === "edited") {
        selectedActivities.value = [...editedActivities.value];
      }
    };

    const resetEditedActivities = () => {
        editableActivities.value = props.pendingActivities.map(activity => ({ ...activity }));
        selectedActivities.value = [];
      };


    const onSubmit = async () => {
      await sendRequest();
      emit('registered');
    };

    watch(
      () => props.pendingActivities,
      (activities) => {
        editableActivities.value = activities.map(activity => ({ ...activity }));
      },
      { immediate: true }
    );

    return {
      date,
      showModal,
      getMaxDate,
      onValidate,
      editableActivities,
      editedActivities,
      selectedActivities,
      reqMsg,
      statusCode,
      getResponseAlert,
      onSubmit,
      toggle,
      clear,
      isEditedActual,
      isSelected,
      applySelection,
      resetEditedActivities
    }
  }
}

</script>
