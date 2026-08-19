import { ref } from 'vue';
import { registerActuals } from '../api/activity';
import { parseError } from '../utils/error';
import { formatFailureMessage } from '../utils/activity';
import axios from 'axios';
import {
  OneActivity,
  RegisterActualResult,
} from '../types/activity';


export const useRegisterActuals = () => {
  const selectedActivities = ref<OneActivity[]>([]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref<number | null>(null);

  const makeMessageByDay = (results: RegisterActualResult[]) => {
    return results
      .map((r) => {
        if (r.result === "success") {
          return `${r.date}の活動時間を${r.actual_time}時間に登録しました`;
        }

        return formatFailureMessage(r.date, "活動時間登録", r.reason);
      })
      .join("\n");
  };

  const sendRequest = async () => {
    try {
      const activities = selectedActivities.value.map(({ date, actual_time }) => ({
        date,
        actual_time,
      }));
      const res = await registerActuals(activities);
      statusCode.value = res.data.error_count === 0 ? 200 : 400;
      reqMsg.value = `【活動時間登録】更新${res.data.success_count}件、エラー${res.data.error_count}件\n`
        + makeMessageByDay(res.data.results);
      selectedActivities.value = [];
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
