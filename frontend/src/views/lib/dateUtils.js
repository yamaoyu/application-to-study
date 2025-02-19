export function getMaxMonth(){
    // 1年後の12月までが範囲となる
    const today = new Date()
    const year = today.getFullYear() + 1
    return `${year}-12`;
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