export type GetMonthlySalaryResponse = {
    base_income: number,
    pay_adjustment: number,
    total_bonus: number,
    total_penalty: number
}

export type MonthlySalarySummary = GetMonthlySalaryResponse & {
    total_income: number
}

export type registerSalaryResponse = {
    year: number,
    month: number,
    salary: number
}