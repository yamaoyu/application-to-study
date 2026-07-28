import { ActivityStatus } from "../types/activity";

export const getResponseAlert = (status: number | null) => {
  // レスポンスのステータスコードに応じたアラートクラスを返す
  if (typeof status == "number" && status >= 200 && status < 300) {
    return 'alert alert-success';
  } else {
    return 'alert alert-warning';
  }
};

export const getActivityAlert = (status: ActivityStatus | null) => {
  // アクティビティのステータスに応じたアラートクラスを返す
  if (status === null) {
    return "alert alert-warning";
  }

  switch (status) {
    case "success":
      return "alert alert-success";
    case "failure":
      return "alert alert-danger";
    case "pending":
      return "alert alert-warning";
  }
};

export const getStatusColors = {
  // アクティビティのステータスに応じた文字の色のクラスを返す
  pending: 'text-dark',
  success: 'text-success fw-bold',
  failure: 'text-danger fw-bold'
};

export const getSalaryColors = (amount: number) => {
  // プラスなら緑、マイナスなら赤、ゼロなら黒の文字の色のクラスを返す
  return amount > 0 ? 'text-success fw-bold' : amount < 0 ? 'text-danger' : 'text-dark';
};

export const STATUS_DICT = {
  // アクティビティのステータスの辞書(key: ステータス, value: 表示文字)
  'success': '達成',
  'failure': '未達成',
  'pending': '未確定'
};

export const getAdjustmentColors = (payAdjustment: number | null) => {
  // TODO: 仮実装でメッセージに「ボーナス」や「ペナルティ」が含まれているかで色を変えているが、将来的にはAPIからのレスポンスでボーナスとペナルティを分けて受け取るようにする
  // ボーナス-ペナルティの結果に応じた文字の色のクラスを返す
  if (typeof payAdjustment == "number" && payAdjustment >= 0) {
    return 'alert alert-success';
  } else {
    return 'alert alert-danger';
  }
};
