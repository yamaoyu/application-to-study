import { ref } from 'vue';
import { registerActuals } from '../api/activity';
import { parseError } from '../utils/error';
import axios from 'axios';
import {
  SendActualActivityParam,
  RegisterActualResult,
  RegisterActualErrorReason,
} from '../types/activity';


export const useRegisterActuals = () => {
  const selectedActivities = ref<SendActualActivityParam[]>([]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref<number | null>(null);

  const errorMessageMap: Record<RegisterActualErrorReason, (date: string) => string> = {
    ACTIVITY_NOT_FOUND: (date: string) => `${date}の活動時間登録に失敗: 目標時間が未登録です`,
    ACTIVITY_ALREADY_FINISHED: (date: string) => `${date}の活動時間登録に失敗: 既に確定されています`,
    SALARY_NOT_FOUND: (date: string) => `${date}の活動時間登録に失敗: 月収が未登録です`,
    UNEXPECTED_ERROR: (date: string) => `${date}の活動時間登録に失敗: 予期せぬエラーが発生しました`,
  };

  const makeMessage = (results: RegisterActualResult[]) => {
    let messages = [];
    for (const r of results) {
      if (r.result === "success") {
        messages.push(`${r.date}の活動時間を${r.actual_time}時間に登録しました`);
        continue;
      } else {
        const messageFn = errorMessageMap[r.reason] || errorMessageMap.UNEXPECTED_ERROR;
        messages.push(messageFn(r.date));
        continue;
      }
    }
    return messages.join("\n");
  };

  const sendRequest = async () => {
    try {
      const res = await registerActuals(selectedActivities.value);
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
