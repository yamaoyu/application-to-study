import { apiClient } from "./client";
import { GetMonthlySalaryResponse, registerSalaryResponse } from "../types/salary";
import type { AxiosResponse } from "axios";

export const postSalary = (
  year: number, month: number, salary: number
): Promise<AxiosResponse<registerSalaryResponse>> => {
  return apiClient.post(
    'incomes/' + year + '/' + month,
    { salary }
  )
};

export const getMonthlySalary = (
  year: number, month: number
): Promise<AxiosResponse<GetMonthlySalaryResponse>> => {
  return apiClient.get(
    'incomes/' + year + '/' + month
  )
};
