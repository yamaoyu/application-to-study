export function generateYearOptions(){
    const today = new Date()
    const yearOptions = [today.getFullYear() - 1, today.getFullYear(), today.getFullYear() + 1]
    return yearOptions;
}

export function generateMonthOptions(){
    const monthOptions = []
    for (let value = 1; value <= 12; value++){
        monthOptions.push(value);
    }
    return monthOptions;
}