import { ref } from 'vue';
import { finishActivies } from '../api/activity';
import { parseError } from '../utils/error';

export const useFinishActivities = () => {
  const selectedActivities = ref([]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const payAdjustment = ref(null);

  const sendRequest = async() => {
    try {
      const dates = selectedActivities.value.map(activity => activity.date);
      const res = await finishActivies(dates);
      if (res.status===200) {
        let msg = '';
        if (res.data.pay_adjustment) msg += `ボーナス-ペナルティ：${res.data.pay_adjustment}\n`;
        if (res.data.total_bonus) msg += `ボーナス：${res.data.total_bonus}\n`;
        if (res.data.total_penalty) msg += `ペナルティ：${res.data.total_penalty}\n`;
        if (res.data.message) msg += res.data.message;
        reqMsg.value = msg;
        selectedActivities.value = [];
        payAdjustment.value = res.data.pay_adjustment;
      };
    } catch (error) {
        reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
        payAdjustment.value = "0";
    }
  }

  return {
    selectedActivities,
    reqMsg,
    payAdjustment,
    sendRequest
  }
};
