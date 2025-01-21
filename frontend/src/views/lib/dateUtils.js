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

export function getToday(){
    // YYYY-MM-DDの形で返す
    const today = new Date()
    const year = today.getFullYear()
    const month = `${today.getMonth()+1}`.padStart(2, '0')
    const day = `${today.getDate()}`.padStart(2, '0')
    return `${year}-${month}-${day}`
}

export function getNextDay(date){
    // YYYY-MM-DDの形で返す
    const newDate = new Date(date)
    newDate.setDate(newDate.getDate() + 1)
    const year = newDate.getFullYear()
    const month = `${newDate.getMonth()+1}`.padStart(2, '0')
    const day = `${newDate.getDate()}`.padStart(2, '0')
    return `${year}-${month}-${day}`
}

export function getPreviousDay(date){
    // YYYY-MM-DDの形で返す
    const newDate = new Date(date)
    newDate.setDate(newDate.getDate() - 1)
    const year = newDate.getFullYear()
    const month = `${newDate.getMonth()+1}`.padStart(2, '0')
    const day = `${newDate.getDate()}`.padStart(2, '0')
    return `${year}-${month}-${day}`
}

export function getNextYear(year){
    return year + 1
}

export function getPreviousYear(year){
    return year - 1
}

export function getNextMonth(month){
    return month + 1
}

export function getPreviousMonth(month){
    return month - 1
}