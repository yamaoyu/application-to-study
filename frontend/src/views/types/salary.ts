type Money = string;

export type GetMonthlySalaryResponse = {
  base_income: Money;
  pay_adjustment: Money;
  total_bonus: Money;
  total_penalty: Money;
};

export type MonthlySalarySummary = GetMonthlySalaryResponse & {
  total_income: Money;
};

export type registerSalaryResponse = {
  year: number;
  month: number;
  salary: Money;
};
