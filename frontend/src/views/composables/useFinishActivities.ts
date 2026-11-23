import { ref } from "vue";
import { finishActivities } from "../api/activity";
import { parseError, getErrorMessageByCode } from "../utils/error";
import { OneActivity, FinishActivityResponse } from "../types/activity";
import { convertTenThousandYenToYen } from "../utils/money";

export const useFinishActivities = () => {
  const selectedActivities = ref<OneActivity[]>([]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const payAdjustment = ref<number | null>(null);

  const makeSuccessMessage = (
    date: string,
    status: string,
    bonus: string,
    penalty: string,
  ) => {
    if (status === "success") {
      return `${date}の活動を終了：ボーナス${Number(bonus)}万円(${convertTenThousandYenToYen(bonus)}円)`;
    } else {
      return `${date}の活動を終了：ペナルティ${Number(penalty)}万円(${convertTenThousandYenToYen(penalty)}円)`;
    }
  };

  const makeMessageByDay = (data: FinishActivityResponse) => {
    const messages: string[] = [];
    const bonusAndPenalty: string = data.pay_adjustment;
    const totalBonus: string = data.total_bonus;
    const totalPenalty: string = data.total_penalty;
    messages.push(
      `ボーナス-ペナルティ：${Number(bonusAndPenalty)}万円(${convertTenThousandYenToYen(bonusAndPenalty)}円)`,
    );
    messages.push(
      `ボーナス：${Number(totalBonus)}万円(${convertTenThousandYenToYen(totalBonus)}円)`,
    );
    messages.push(
      `ペナルティ：${Number(totalPenalty)}万円(${convertTenThousandYenToYen(totalPenalty)}円)`,
    );
    for (const result of data.results) {
      if (result.result === "success") {
        messages.push(
          `${makeSuccessMessage(result.date, result.status, result.bonus, result.penalty)}`,
        );
      } else {
        const message = getErrorMessageByCode(result.reason);
        messages.push(`${result.date}の活動終了に失敗: ${message}`);
      }
    }
    return messages.join("\n");
  };

  const sendRequest = async () => {
    try {
      const dates = selectedActivities.value.map((activity) => activity.date);
      const res = await finishActivities(dates);
      reqMsg.value =
        `【活動終了】終了済み${res.data.success_count}件、エラー${res.data.error_count}件\n` +
        makeMessageByDay(res.data);
      selectedActivities.value = [];
      payAdjustment.value = Number(res.data.pay_adjustment);
    } catch (error) {
      reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
      payAdjustment.value = null;
    }
  };

  return {
    selectedActivities,
    reqMsg,
    payAdjustment,
    sendRequest,
  };
};
