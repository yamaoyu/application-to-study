import { ref } from 'vue';
import { registerTargets } from '../api/activity';
import { parseError } from '../utils/error';

export const useRegisterTargets = () => {
  const targetActivities = ref([{ date: '', target_time: 0.5 }]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref(null);

  const sendRequest = async() => {
    try {
      const res = await registerTargets(targetActivities.value);
      statusCode.value = res.status;
      if (res.status===201) {
        reqMsg.value = res.data.message;
        targetActivities.value = [{ date: '', target_time: 0.5 }];
      };
    } catch (error) {
        reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
        statusCode.value = error.response?.status ?? null;
    }
  }

  return {
    targetActivities,
    reqMsg,
    statusCode,
    sendRequest
  }

};

export const addTargetActivity = (targetActivities) => {
  targetActivities.push({ date: '', target_time: 0.5 });
};

export const removeTargetActivity = (targetActivities, index) => {
  if (targetActivities.length > 1) {
      targetActivities.splice(index, 1);
  } else {
      targetActivities[0].target_time = 0.5;
      targetActivities[0].date = "";
  }
};
