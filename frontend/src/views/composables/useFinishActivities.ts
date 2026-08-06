import { ref } from 'vue';
import { finishActivities } from '../api/activity';
import { parseError, getErrorMessageByCode } from '../utils/error';
import {
  OneActivity,
  FinishActivityResponse
} from '../types/activity';


export const useFinishActivities = () => {
  const selectedActivities = ref<OneActivity[]>([]);
  const reqMsg = ref<string>(""); // リクエスト結果を表示するためのメッセージ
  const payAdjustment = ref<number | null>(null);

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

  const makeMsg = (data: FinishActivityResponse) => {
    const messages: string[] = [];
    const bonusAndPenalty: number = data.pay_adjustment;
    const totalBonus: number = data.total_bonus;
    const totalPenalty: number = data.total_penalty;
    messages.push(`ボーナス-ペナルティ：${bonusAndPenalty}万円(${convert_ten_thousand_yen_to_yen(bonusAndPenalty)}円)`);
    messages.push(`ボーナス：${totalBonus}万円(${convert_ten_thousand_yen_to_yen(totalBonus)}円)`);
    messages.push(`ペナルティ：${totalPenalty}万円(${convert_ten_thousand_yen_to_yen(totalPenalty)}円)`);
    for (const result of data.results) {
      if (result.result === 'success') {
        messages.push(`${makeSuccessMessage(result.date, result.status, result.bonus, result.penalty)}`);
      } else {
        const message = getErrorMessageByCode(result.reason);
        messages.push(`${result.date}の活動終了に失敗: ${message}`);
      }
    }
    return messages.join("\n");
  }

  const sendRequest = async () => {
    try {
      const dates = selectedActivities.value.map(activity => activity.date);
      const res = await finishActivities(dates);
      if (res.status === 200) {
        reqMsg.value = makeMsg(res.data);
        selectedActivities.value = [];
        payAdjustment.value = res.data.pay_adjustment;
      };
    } catch (error) {
      reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
      payAdjustment.value = null;
    }
  }

  return {
    selectedActivities,
    reqMsg,
    payAdjustment,
    sendRequest
  }
};
