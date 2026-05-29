import { ref } from 'vue';
import { registerActuals } from '../api/activity';
import { parseError } from '../utils/error';

export const useRegisterActuals = () => {
  const selectedActivities = ref([]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref(null);

  const resultMessageMap = {
    success: (date, actual_time) => `${date}の活動時間を${actual_time}時間に登録しました`,
    activity_not_found: (date) => `${date}の活動時間登録に失敗: 目標時間が未登録です`,
    activity_already_finished: (date) => `${date}の活動時間登録に失敗: 既に確定されています`,
    income_not_found: (date) => `${date}の活動時間登録に失敗: 月収が未登録です`,
    unexpected_error: (date) => `${date}の活動時間登録に失敗: 予期せぬエラーが発生しました`,
  };

  const makeMessage = (results) => {
    let messages = [];
    for (const r of results) {
      if (r.result === "success") {
        messages.push(resultMessageMap.success(r.date, r.actual_time));
        continue;
      } else if (r.result === "error") {
        const messageFn = resultMessageMap[r.reason] || resultMessageMap.unexpected_error;
        messages.push(messageFn(r.date));
        continue;
      } else {
        messages.push(`${r.date}の活動時間登録に失敗: 不明なエラーが発生しました`);
        continue;
      }
    }
    return messages.join("\n");
  };

  const sendRequest = async() => {
    try {
      const res = await registerActuals(selectedActivities.value);
      statusCode.value = res.status;
      if (res.status===200) {
        reqMsg.value = makeMessage(res.data.results);
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
