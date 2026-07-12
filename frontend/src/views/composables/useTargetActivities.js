import { ref } from 'vue';
import { registerTargets } from '../api/activity';
import { parseError } from '../utils/error';

export const useRegisterTargets = () => {
  const targetActivities = ref([{ date: '', target_time: 0.5 }]);
  const reqMsg = ref(""); // リクエスト結果を表示するためのメッセージ
  const statusCode = ref(null);

  const resultMessageMap = {
    success: (date, target_time) => `${date}の目標時間を${target_time}時間に登録しました`,
    TARGET_TIME_ALREADY_REGISTERED: (date) => `${date}の目標時間登録に失敗: 既に登録されています`,
    SALARY_NOT_FOUND: (date) => `${date}の目標時間登録に失敗: 月収が未登録です`,
    UNEXPECTED_ERROR: (date) => `${date}の目標時間登録に失敗: 予期せぬエラーが発生しました`,
  };

  const makeMessage = (results) => {
    let messages = [];
    for (const r of results) {
      if (r.result === "success") {
        messages.push(resultMessageMap.success(r.date, r.target_time));
        continue;
      } else if (r.result === "error") {
        const messageFn = resultMessageMap[r.reason] || resultMessageMap.UNEXPECTED_ERROR;
        messages.push(messageFn(r.date));
        continue;
      } else {
        messages.push(`${r.date}の目標時間登録に失敗: 不明なエラーが発生しました`);
        continue;
      }
    }
    return messages.join("\n");
  };

  const sendRequest = async() => {
    try {
      const res = await registerTargets(targetActivities.value);
      statusCode.value = res.status;
      if (res.status===201) {
        reqMsg.value = makeMessage(res.data.results);
        targetActivities.value = [{ date: '', target_time: 0.5 }];
      };
    } catch (error) {
      if (error.response?.data?.results) {
        reqMsg.value = makeMessage(error.response.data.results);
      } else {
        reqMsg.value = parseError(error, "活動時間の登録に失敗しました");
      }
      statusCode.value = error.response?.status ?? null;
    }
  }

  return {
    targetActivities,
    reqMsg,
    statusCode,
    sendRequest
  }

};

export const addTargetActivity = (targetActivities) => {
  targetActivities.push({ date: '', target_time: 0.5 });
};

export const removeTargetActivity = (targetActivities, index) => {
  if (targetActivities.length > 1) {
      targetActivities.splice(index, 1);
  } else {
      targetActivities[0].target_time = 0.5;
      targetActivities[0].date = "";
  }
};
