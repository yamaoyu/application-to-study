import { ref } from 'vue';
import { registerActuals } from '../api/activity';
import { parseError } from '../utils/error';

export const useRegisterActuals = () => {
  const selectedActivities = ref([]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref(null);

  const sendRequest = async() => {
    try {
      const res = await registerActuals(selectedActivities.value);
      statusCode.value = res.status;
      if (res.status===200) {
        reqMsg.value = res.data.message;
        selectedActivities.value = [];
      };
    } catch (error) {
        reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
        statusCode.value = error.response?.status ?? null;
    }
  };

  return {
    selectedActivities,
    reqMsg,
    statusCode,
    sendRequest
  }
};
