import { ref } from 'vue';
import { registerTargets } from '../api/activity';
import { parseError } from '../utils/error';
import axios from 'axios';
import {
  SendTargetActivityParam,
  RegisterTargetResult,
  RegisterTargetErrorReason
} from '../types/activity';


export const useRegisterTargets = () => {
  const targetActivities = ref<SendTargetActivityParam[]>([{ date: '', target_time: 0.5 }]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref<number | null>(null);

  const resultMessageMap: Record<RegisterTargetErrorReason, (date: string) => string> = {
    TARGET_TIME_ALREADY_REGISTERED: (date: string) => `${date}の目標時間登録に失敗: 既に登録されています`,
    SALARY_NOT_FOUND: (date: string) => `${date}の目標時間登録に失敗: 月収が未登録です`,
    UNEXPECTED_ERROR: (date: string) => `${date}の目標時間登録に失敗: 予期せぬエラーが発生しました`,
  };

  const makeMessage = (results: RegisterTargetResult[]) => {
    let messages = [];
    for (const r of results) {
      if (r.result === "success") {
        messages.push(`${r.date}の目標時間を${r.target_time}時間に登録しました`);
        continue;
      } else {
        const messageFn = resultMessageMap[r.reason] || resultMessageMap.UNEXPECTED_ERROR;
        messages.push(messageFn(r.date));
        continue;
      }
    }
    return messages.join("\n");
  };

  const sendRequest = async () => {
    try {
      const res = await registerTargets(targetActivities.value);
      statusCode.value = res.status;
      if (res.status === 201) {
        reqMsg.value = makeMessage(res.data.results);
        targetActivities.value = [{ date: '', target_time: 0.5 }];
      };
    } catch (error: unknown) {
      reqMsg.value = parseError(error, "活動時間の登録に失敗しました")
      if (axios.isAxiosError(error)) {
        statusCode.value = error.response?.status ?? null;
      } else {
        statusCode.value = null;
      }
    }
  };

  return {
    targetActivities,
    reqMsg,
    statusCode,
    sendRequest
  };
};

export const addTargetActivity = (targetActivities: SendTargetActivityParam[]) => {
  targetActivities.push({ date: '', target_time: 0.5 });
};

export const removeTargetActivity = (targetActivities: SendTargetActivityParam[], index: number) => {
  if (targetActivities.length > 1) {
    targetActivities.splice(index, 1);
  } else {
    targetActivities[0].target_time = 0.5;
    targetActivities[0].date = "";
  }
};
