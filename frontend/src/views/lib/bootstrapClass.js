export const statusClass = {
    pending: 'text-dark',
    success: 'text-success fw-bold',
    failure: 'text-danger fw-bold'};

export const resultClass = (response) => {
    if (response.data.pay_adjustment > 0) {
        return 'text-success';
    } else if (response.data.pay_adjustment < 0) {
        return 'text-danger';
    } else {
        return 'text-dark';
    }
}

export const activityAlertClass = (response) => {
    if (!response) {
        // 未登録の場合
        return 'alert-warning';
    } else if (response.data.status === 'success') {
        return 'alert-success';
    } else if (response.data.status === 'failure') {
        return 'alert-danger';
    } else {
        // 登録はあるがステータスが未確定の場合
        return 'alert-warning';
    }
}