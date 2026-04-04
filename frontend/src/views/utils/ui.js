export const getResponseAlert = (status) => {
  // レスポンスのステータスコードに応じたアラートクラスを返す
  if (status >= 200 && status < 300) {
    return 'alert alert-success';
  } else {
    return 'alert alert-warning';
  }
};

export const getActivityAlert = (status) => {
  // アクティビティのステータスに応じたアラートクラスを返す
  if (!status) {
    // 未登録の場合
    return 'alert alert-warning';
  } else if (status === 'success') {
    return 'alert alert-success';
  } else if (status === 'failure') {
    return 'alert alert-danger';
  } else {
    // 登録はあるがステータスが未確定(pending)の場合
    return 'alert alert-warning';
  }
};

export const getStatusColors = {
  // アクティビティのステータスに応じた文字の色のクラスを返す
  pending: 'text-dark',
  success: 'text-success fw-bold',
  failure: 'text-danger fw-bold'
};

export const STATUS_DICT = {
  // アクティビティのステータスの辞書(key: ステータス, value: 表示文字)
  'success': '達成',
  'failure': '未達成',
  'pending': '未確定'
};

export const getAdjustmentColors = (message) => {
  // TODO: 仮実装でメッセージに「ボーナス」や「ペナルティ」が含まれているかで色を変えているが、将来的にはAPIからのレスポンスでボーナスとペナルティを分けて受け取るようにする
  // ボーナス-ペナルティの結果に応じた文字の色のクラスを返す
  if (!message.includes("-")) {
      return 'alert alert-success';
  } else {
      return 'alert alert-danger';
  }
};
