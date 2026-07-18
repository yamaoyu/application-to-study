import { ref } from 'vue';
import { finishActivies } from '../api/activity';
import { parseError } from '../utils/error';

type finishDetail =
  | {
    "date": string,
    "reason": null,
    "result": "success",
    "bonus": number,
    "penalty": number,
    "status": "success" | "error"
  }
  | {
    "date": string,
    "reason": ErrorReason,
    "result": "error",
    "bonus": null,
    "penalty": null,
    "status": null
  }

type finishResult = {
  "pay_adjustment": number,
  "total_bonus": number,
  "total_penalty": number,
  "results": finishDetail[]
}

type activity = {
  "date": string
}

type ErrorReason =
  | "ACTIVITY_NOT_FOUND"
  | "ACTIVITY_ALREADY_FINISHED"
  | "SALARY_NOT_FOUND"
  | "UNEXPECTED_ERROR";

export const useFinishActivities = () => {
  const selectedActivities = ref<activity[]>([]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const payAdjustment = ref<number | null>(null);

  const resultMessageMap = {
    ACTIVITY_NOT_FOUND: (date: string) => `${date}の活動終了に失敗: 目標時間が未登録です`,
    ACTIVITY_ALREADY_FINISHED: (date: string) => `${date}の活動終了に失敗: 既に確定されています`,
    SALARY_NOT_FOUND: (date: string) => `${date}の活動終了に失敗: 月収が未登録です`,
    UNEXPECTED_ERROR: (date: string) => `${date}の活動終了に失敗: 予期せぬエラーが発生しました`,
  };

  const convert_ten_thousand_yen_to_yen = (amount: number) => {
    // 金額を万円から円に変換する関数
    // 例: 1.5 -> 15000、-0.5 -> -5000
    return Math.round(amount * 10000);
  };

  const makeSuccessMessage = (date: string, status: string, bonus: number, penalty: number) => {
    if (status === 'success') {
      return `${date}の活動を終了：ボーナス${bonus}万円(${convert_ten_thousand_yen_to_yen(bonus)}円)`;
    } else {
      return `${date}の活動を終了：ペナルティ${penalty}万円(${convert_ten_thousand_yen_to_yen(penalty)}円)`;
    }
  };

  const makeErrorMessage = (date: string, reason: ErrorReason) => {
    const messageFn = resultMessageMap[reason] || resultMessageMap.UNEXPECTED_ERROR;
    return messageFn(date);
  };

  const makeMsg = (data: finishResult) => {
    let messages = [];
    const bonusAndPenalty = data.pay_adjustment;
    const totalBonus = data.total_bonus;
    const totalPenalty = data.total_penalty;
    if (data.pay_adjustment) messages.push(`ボーナス-ペナルティ：${bonusAndPenalty}万円(${convert_ten_thousand_yen_to_yen(bonusAndPenalty)}円)`);
    if (data.total_bonus) messages.push(`ボーナス：${totalBonus}万円(${convert_ten_thousand_yen_to_yen(totalBonus)}円)`);
    if (data.total_penalty) messages.push(`ペナルティ：${totalPenalty}万円(${convert_ten_thousand_yen_to_yen(totalPenalty)}円)`);
    for (const result of data.results) {
      if (result.result === 'success') {
        messages.push(`${makeSuccessMessage(result.date, result.status, result.bonus, result.penalty)}`);
      } else {
        const message = makeErrorMessage(result.date, result.reason)
        messages.push(message);
      }
    }
    return messages.join("\n");
  }

  const sendRequest = async () => {
    try {
      const dates = selectedActivities.value.map(activity => activity.date);
      const res = await finishActivies(dates);
      if (res.status === 200) {
        reqMsg.value = makeMsg(res.data);
        selectedActivities.value = [];
        payAdjustment.value = res.data.pay_adjustment;
      };
    } catch (error) {
      reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
      payAdjustment.value = 0;
    }
  }

  return {
    selectedActivities,
    reqMsg,
    payAdjustment,
    sendRequest
  }
};
