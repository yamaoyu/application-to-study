import {
  SendTargetActivityParam,
  RegisterTargetErrorReason,
  RegisterActualErrorReason,
  FinishActivityErrorReason
} from "../types/activity";
import { getErrorMessageByCode } from "./error";

export const validateTargetTime = (time: number) => {
  if (time === null || time === undefined) {
    return "時間を入力してください";
  }

  if (time < 0.5) {
    return "時間は0.5時間以上入力してください";
  }

  if (time * 2 % 1 !== 0) {
    return "時間は0.5時間単位で入力してください";
  }

  return null
};

export const hasDuplicateDate = (dates: string[], date: string) => {
  return dates.filter(d => d && d === date).length > 1;
};

export const isValidActivities = (activities: SendTargetActivityParam[]) => {
  return !activities.some(a => !a.date || !a.target_time)
};

export const validateActualTime = (time: number) => {
  if (time === null || time === undefined) {
    return "時間を入力してください";
  }

  if (time * 2 % 1 !== 0) {
    return "時間は0.5時間単位で入力してください";
  }

  return null
};

export const formatFailureMessage = (
  date: string,
  actionLabel: "目標時間登録" | "活動時間登録",
  reason: RegisterTargetErrorReason | RegisterActualErrorReason | FinishActivityErrorReason
) => {
  return `${date}の${actionLabel}に失敗: ${getErrorMessageByCode(reason)}`;
};
