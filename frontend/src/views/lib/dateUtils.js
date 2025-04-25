export const MONTH_DICT = {
    "jan": '1月',
    "feb": '2月',
    "mar": '3月',
    "apr": '4月',
    "may": '5月',
    "jun": '6月',
    "jul": '7月',
    "aug": '8月',
    "sep": '9月',
    "oct": '10月',
    "nov": '11月',
    "dec": '12月'
}

export function getMaxYear(){
    // 1年後までが範囲となる
    const today = new Date()
    const year = today.getFullYear() + 1
    return year
}

export function getMaxMonth(){
    // 1年後の12月までが範囲となる
    return `${getMaxYear()}-12`
}

export function getMaxDate(){
    // 1年後の12月31日までが範囲となる
    return `${getMaxYear()}-12-31`;
}

export function changeDate(date, message){
    const increaseDay = async(step) => {
        if (date.value !== '') {
            message.value = ""
            // YYYY-MM-DDの形にする
            const newDate = new Date(date.value)
            newDate.setDate(newDate.getDate() + step)
            const year = newDate.getFullYear()
            const month = `${newDate.getMonth()+1}`.padStart(2, '0')
            const day = `${newDate.getDate()}`.padStart(2, '0')
            date.value = `${year}-${month}-${day}`
        } else{
            message.value = "日付が指定されていません"
        }
    }

    return {
        increaseDay
    }
}

export function changeYear(selectedMonth){
    const increaseYear = async(step) => {
        // YYYY-MMの形を受け取り、年にstepを足す
        const [year, month] = selectedMonth.value.split('-').map(Number)
        let newDate = new Date(year + step, month)
        selectedMonth.value = newDate.toISOString().slice(0, 7)
    }

    return {
        increaseYear
    }
}

export function changeMonth(selectedMonth){
    const increaseMonth = async(step) => {
        const [year, month] = selectedMonth.value.split('-').map(Number)
        let newDate = new Date(year, month + step)
        selectedMonth.value = newDate.toISOString().slice(0, 7)
    }

    return {
        increaseMonth
    }
}

export function getToday(){
    const today = new Date()
    const year = today.getFullYear()
    const month = `${today.getMonth()+1}`.padStart(2, '0')
    const day = `${today.getDate()}`.padStart(2, '0')
    return `${year}-${month}-${day}`
}

export function getThisMonth(){
    const today = new Date()
    const year = today.getFullYear()
    const month = `${today.getMonth()+1}`.padStart(2, '0')
    return `${year}-${month}`
}

export function getThisYear(){
    const today = new Date()
    const year = today.getFullYear()
    return year
}