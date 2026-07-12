import { ref } from 'vue';
import { finishActivies } from '../api/activity';
import { parseError } from '../utils/error';

export const useFinishActivities = () => {
  const selectedActivities = ref([]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const payAdjustment = ref(null);

  const resultMessageMap = {
    success: (date, yen) => `${date}の活動を終了：ボーナス${yen}万円(${convert_ten_thousand_yen_to_yen(yen)}円)`,
    failure: (date, yen) => `${date}の活動を終了：ペナルティ${yen}万円(${convert_ten_thousand_yen_to_yen(yen)}円)`,
    ACTIVITY_NOT_FOUND: (date) => `${date}の活動終了に失敗: 目標時間が未登録です`,
    ACTIVITY_ALREADY_FINISHED: (date) => `${date}の活動終了に失敗: 既に確定されています`,
    SALARY_NOT_FOUND: (date) => `${date}の活動終了に失敗: 月収が未登録です`,
    UNEXPECTED_ERROR: (date) => `${date}の活動終了に失敗: 予期せぬエラーが発生しました`,
  };

  const convert_ten_thousand_yen_to_yen = (amount) => {
    // 金額を万円から円に変換する関数
    // 例: 1.5 -> 15000、-0.5 -> -5000
    return Math.round(amount * 10000);
  };

  const makeSuccessMessage = (date, status, bonus, penalty) => {
    if (status === 'success') {
      return resultMessageMap.success(date, bonus);
    } else {
      return resultMessageMap.failure(date, penalty);
    }
  };

  const makeErrorMessage = (date, reason) => {
    const messageFn = resultMessageMap[reason] || resultMessageMap.UNEXPECTED_ERROR;
    return messageFn(date);
  };

  const makeMsg = (data) => {
    let msg = '';
    const bonusAndPenalty = data.pay_adjustment;
    const totalBonus = data.total_bonus;
    const totalPenalty = data.total_penalty;
    if (data.pay_adjustment) msg += `ボーナス-ペナルティ：${bonusAndPenalty}万円(${convert_ten_thousand_yen_to_yen(bonusAndPenalty)}円)\n`;
    if (data.total_bonus) msg += `ボーナス：${totalBonus}万円(${convert_ten_thousand_yen_to_yen(totalBonus)}円)\n`;
    if (data.total_penalty) msg += `ペナルティ：${totalPenalty}万円(${convert_ten_thousand_yen_to_yen(totalPenalty)}円)\n`;
    for (const result of data.results) {
      if (result.result === 'success') {
        msg += `${makeSuccessMessage(result.date, result.status, result.bonus, result.penalty)}\n`;
      } else if (result.result === 'error') {
        msg += `${makeErrorMessage(result.date, result.reason)}\n`;
      } else {
        msg += `${makeErrorMessage(result.date, 'UNEXPECTED_ERROR')}\n`;
      }
    }
    return msg;
  }

  const sendRequest = async() => {
    try {
      const dates = selectedActivities.value.map(activity => activity.date);
      const res = await finishActivies(dates);
      if (res.status===200) {
        reqMsg.value = makeMsg(res.data);
        selectedActivities.value = [];
        payAdjustment.value = res.data.pay_adjustment;
      };
    } catch (error) {
      reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
      payAdjustment.value = "0";
    }
  }

  return {
    selectedActivities,
    reqMsg,
    payAdjustment,
    sendRequest
  }
};
