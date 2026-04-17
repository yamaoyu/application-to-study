import { apiClient } from "./client";

export const postSalary = (year, month, salary) => {
  return apiClient.post(
    'incomes/' + year + '/' + month,
    { salary }
  )
};

export const getMonthlySalary = (year, month) => {
  return apiClient.get(
    'incomes/' + year + '/' + month
  )
};
