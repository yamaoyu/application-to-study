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
