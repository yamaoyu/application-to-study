import { ref } from 'vue';
import { finishActivies } from '../api/activity';
import { parseError } from '../utils/error';

export const useFinishActivities = () => {
  const selectedActivities = ref([]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const payAdjustment = ref(null);

  const convert_ten_thousand_yen_to_yen = (amount) => {
    // 金額を万円から円に変換する関数
    // 例: 1.5 -> 15000、-0.5 -> -5000
    return Math.round(amount * 10000);
  };

  const makeMsg = (res) => {
    let msg = '';
    const bonusAndPenalty = res.data.pay_adjustment;
    const totalBonus = res.data.total_bonus;
    const totalPenalty = res.data.total_penalty;
    if (res.data.pay_adjustment) msg += `ボーナス-ペナルティ：${bonusAndPenalty}万円(${convert_ten_thousand_yen_to_yen(bonusAndPenalty)}円)\n`;
    if (res.data.total_bonus) msg += `ボーナス：${totalBonus}万円(${convert_ten_thousand_yen_to_yen(totalBonus)}円)\n`;
    if (res.data.total_penalty) msg += `ペナルティ：${totalPenalty}万円(${convert_ten_thousand_yen_to_yen(totalPenalty)}円)\n`;
    if (res.data.message) msg += res.data.message;
    for (const result of res.data.results) {
      msg += `${result.date}の活動を終了：`;
      if (result.status === 'success') {
        msg += `ボーナス${result.bonus}万円(${convert_ten_thousand_yen_to_yen(result.bonus)}円)\n`;
      } else {
        msg += `ペナルティ${result.penalty}万円(${convert_ten_thousand_yen_to_yen(result.penalty)}円)\n`;
      }
    }
    for (const error of res.data.errors) {
      msg += `${error.date}の活動終了に失敗:${error.message}\n`;
    }
    return msg;
  }

  const sendRequest = async() => {
    try {
      const dates = selectedActivities.value.map(activity => activity.date);
      const res = await finishActivies(dates);
      if (res.status===200) {
        reqMsg.value = makeMsg(res);
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
