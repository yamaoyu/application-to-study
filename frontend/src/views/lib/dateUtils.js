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

export function changeDate(date, message){
    const insertToday = async() => {
        message.value = ""
        // YYYY-MM-DDの形にする
        const today = new Date()
        const year = today.getFullYear()
        const month = `${today.getMonth()+1}`.padStart(2, '0')
        const day = `${today.getDate()}`.padStart(2, '0')
        date.value = `${year}-${month}-${day}`
    }

    const decreaseOneDay = async() => {
        if (date.value) {
            message.value = ""
            // YYYY-MM-DDの形にする
            const newDate = new Date(date.value)
            newDate.setDate(newDate.getDate() - 1)
            const year = newDate.getFullYear()
            const month = `${newDate.getMonth()+1}`.padStart(2, '0')
            const day = `${newDate.getDate()}`.padStart(2, '0')
            date.value = `${year}-${month}-${day}`
        } else {
            message.value = "日付が指定されていません"
        }
    }

    const increaseOneDay = async() => {
        if (date.value !== '') {
            message.value = ""
            // YYYY-MM-DDの形にする
            const newDate = new Date(date.value)
            newDate.setDate(newDate.getDate() + 1)
            const year = newDate.getFullYear()
            const month = `${newDate.getMonth()+1}`.padStart(2, '0')
            const day = `${newDate.getDate()}`.padStart(2, '0')
            date.value = `${year}-${month}-${day}`
        } else{
            message.value = "日付が指定されていません"
        }
    }

    return {
        insertToday,
        decreaseOneDay,
        increaseOneDay
    }
}

export function changeYear(year, message){
    const insertThisYear = async() =>{
        year.value = new Date().getFullYear()
        message.value = ""
    }

    const decreaseOneYear = async() => {
        if (year.value === 2024){
            message.value = "2024年より前は選択できません"
        } else if (year.value) {
            year.value -= 1;
            message.value = "";
        } else {
            message.value = "年が指定されていません"
        }
    }

    const increaseOneYear = async() => {
        const today = new Date()
        const nextYeat = today.getFullYear() + 1
        if (year.value === nextYeat){
            message.value = nextYeat + "年より後は選択できません";
        } else if (year.value) {
            year.value += 1;
            message.value = "";
        } else {
            message.value = "年が指定されていません"
        }
    }

    return {
        insertThisYear,
        decreaseOneYear,
        increaseOneYear
    }
}

export function changeMonth(month, year, message){
    const insertThisMonth = async() =>{
        month.value = new Date().getMonth() + 1
        message.value = ""
    }

    const decreaseOneMonth = async() => {
        if (month.value && year.value) {
            if (month.value === 1 && year.value > 2024) {
                month.value = 12;
                year.value -= 1;
                message.value = "";
            } else if (month.value != 1 && year.value >= 2024) {
                month.value -= 1;
                message.value = "";
            } else {
                message.value = "2024年より前は選択できません";
            }
        } else if (!month.value) {
            message.value = "月が指定されていません"
        } else {
            message.value = "年が指定されていません"
        }
    }

    const increaseOneMonth = async() => {
        const today = new Date()
        const nextYeat = today.getFullYear() + 1
        if (month.value && year.value) {
            if (month.value === 12 && year.value < nextYeat) {
                month.value = 1;
                year.value += 1;
            } else if (month.value != 12 && year.value <= nextYeat) {
                month.value += 1;
                message.value = "";
            } else {
                message.value = nextYeat + "年より後は選択できません";
            }
        } else if(!month.value) {
            message.value = "月が指定されていません"
        } else {
            message.value = "年が指定されていません"
        }
    }

    return {
        insertThisMonth,
        decreaseOneMonth,
        increaseOneMonth
    }
}