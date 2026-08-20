import { ref } from 'vue';
import { registerTargets } from '../api/activity';
import { parseError } from '../utils/error';
import { formatFailureMessage } from '../utils/activity';
import axios from 'axios';
import {
  SendTargetActivityParam,
  RegisterTargetResult
} from '../types/activity';


export const useRegisterTargets = () => {
  const targetActivities = ref<SendTargetActivityParam[]>([{ date: '', target_time: 0.5 }]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref<number | null>(null);

  const makeMessageByDay = (results: RegisterTargetResult[]) => {
    return results
      .map((r) => {
        if (r.result === "success") {
          return `${r.date}の目標時間を${r.target_time}時間に登録しました`;
        }

        return formatFailureMessage(r.date, "目標時間登録", r.reason);
      })
      .join("\n");
  };

  const sendRequest = async () => {
    try {
      const res = await registerTargets(targetActivities.value);
      statusCode.value = res.data.error_count === 0 ? 200 : 400;
      reqMsg.value = `【目標時間登録】登録${res.data.success_count}件、エラー${res.data.error_count}件\n`
        + makeMessageByDay(res.data.results);
      targetActivities.value = [{ date: '', target_time: 0.5 }];
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
