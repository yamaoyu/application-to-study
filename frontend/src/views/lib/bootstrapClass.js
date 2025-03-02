export const getStatusColors = {
    // アクティビティのステータスに応じた文字の色のクラスを返す
    pending: 'text-dark',
    success: 'text-success fw-bold',
    failure: 'text-danger fw-bold'};

export const getAdjustmentColors = (response) => {
    // ボーナス-ペナルティの結果に応じた文字の色のクラスを返す
    if (response.data.pay_adjustment > 0) {
        return 'text-success';
    } else if (response.data.pay_adjustment < 0) {
        return 'text-danger';
    } else {
        return 'text-dark';
    }
}

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
        // 登録はあるがステータスが未確定の場合
        return 'alert alert-warning';
    }
}

export const getResponseAlert = (status) => {
    // レスポンスのステータスコードに応じたアラートクラスを返す
    if (status >= 200 && status < 300) {
        return 'alert alert-success';
    } else {
        return 'alert alert-warning';
    }
}