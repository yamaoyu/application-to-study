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