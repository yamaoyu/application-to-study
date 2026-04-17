<template>
  <div>
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
          @click="toggleAll(pendingActivities)"
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
            @click="toggle(activity)"
            :class="{ 'table-active': isSelected(activity) }"
          >
          <td :data-testid="`is-selected-finish-${index}`">
            <input 
              class="form-check-input" 
              type="checkbox"
              :value="activity"
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
          @click="showModal = true"
          :disabled="selectedActivities.length === 0"
          data-testid="finish-multi"
      >
          まとめて終了
      </button>
    </div>
    <div v-else class="mt-3 alert alert-warning">確定可能な活動がありません</div>
  </div>
  <div class="container d-flex justify-content-center" v-if="reqMsg" data-testid="reqMsg">
      <p class="mt-3 col-12" :class="getAdjustmentColors(payAdjustment)">{{ reqMsg }}</p>
  </div>

  <!-- モーダルコンポーネントで登録前の確認 -->
  <BModal v-model="showModal" title="活動時間の確定" ok-title="はい" cancel-title="いいえ" @ok="onSubmit" data-testid="modal-show">
    <p>選択した日の活動を終了しますか？</p>
  </BModal>
</template>

<script>
import { ref, watch } from 'vue';
import { BModal, BCard, BCardText } from 'bootstrap-vue-next';
import { useFinishActivities } from './composables/useFinishActvities';
import { getAdjustmentColors } from './utils/ui';
import { useSelection } from './composables/useSelection';

export default {
  props: {
    pendingActivities: {
      default: () => []
    }
  },

  components: {
    BModal,
    BCard,
    BCardText
  },

  emits: ['registered'],

  setup(props, { emit }) {
    const pendingActivities = ref([]);
    const showModal = ref(false);
    const { selectedActivities, reqMsg, payAdjustment, sendRequest } = useFinishActivities();
    const { isSelected, toggle, clear, toggleAll } = useSelection(selectedActivities);

    watch(
      () => props.pendingActivities,
      (activities) => {
        pendingActivities.value = activities.map(activity => ({ ...activity }));
      },
      { immediate: true }
    );

    const onSubmit = async () => {
      await sendRequest();
      emit('registered');
    };


    return {
      selectedActivities,
      reqMsg,
      payAdjustment,
      sendRequest,
      pendingActivities,
      showModal,
      onSubmit,
      getAdjustmentColors,
      isSelected,
      toggle,
      clear,
      toggleAll
    }
  }
}

</script>
