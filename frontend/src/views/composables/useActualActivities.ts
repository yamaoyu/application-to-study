import { ref } from 'vue';
import { registerActuals } from '../api/activity';
import { parseError, getErrorMessageByCode } from '../utils/error';
import axios from 'axios';
import {
  OneActivity,
  RegisterActualResult,
} from '../types/activity';


export const useRegisterActuals = () => {
  const selectedActivities = ref<OneActivity[]>([]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref<number | null>(null);

  const makeMessage = (results: RegisterActualResult[]) => {
    const messages = [];
    for (const r of results) {
      if (r.result === "success") {
        messages.push(`${r.date}の活動時間を${r.actual_time}時間に登録しました`);
        continue;
      } else {
        const message = getErrorMessageByCode(r.reason);
        messages.push(`${r.date}の活動時間登録に失敗: ${message}`);
        continue;
      }
    }
    return messages.join("\n");
  };

  const sendRequest = async () => {
    try {
      const activities = selectedActivities.value.map(({ date, actual_time }) => ({
        date,
        actual_time,
      }));
      const res = await registerActuals(activities);
      statusCode.value = res.status;
      if (res.status === 200) {
        reqMsg.value = makeMessage(res.data.results);
        selectedActivities.value = [];
      };
    } catch (error: unknown) {
      reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
      if (axios.isAxiosError(error)) {
        statusCode.value = error.response?.status ?? null;
      } else {
        statusCode.value = null;
      }
    }
  };

  return {
    selectedActivities,
    reqMsg,
    statusCode,
    sendRequest
  }
};
