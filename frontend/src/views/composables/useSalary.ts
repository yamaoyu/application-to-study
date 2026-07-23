import { ref } from "vue";
import { getMonthlySalary, postSalary } from "../api/salary";
import { getThisMonth } from "../utils/date";
import { parseError } from "../utils/error";
import { MonthlySalarySummary } from "../types/salary";
import axios from 'axios';

export const useFetchMonthlySalary = () => {
  const fetchMsg = ref<string>('');
  const fetchSalarySummary = ref<MonthlySalarySummary>();
  const fetchSalaryStatus = ref<number>();

  const fetchMonthlySalary = async (year: number, month: number) => {
    try {
      const res = await getMonthlySalary(year, month);
      // total_incomeはbase_income+pay_adjustmentで計算できるためフロントエンドで計算している
      const totalIncome = Math.round((res.data.base_income + res.data.pay_adjustment) * 100) / 100;
      fetchSalarySummary.value = {
        ...res.data,
        total_income: totalIncome
      }
      fetchSalaryStatus.value = res.status
      fetchMsg.value = "";
    } catch (error: unknown) {
      fetchMsg.value = parseError(error, "月収の取得に失敗しました");
      fetchSalarySummary.value = undefined;
      if (axios.isAxiosError(error)) {
        fetchSalaryStatus.value = error.response?.status;
      } else {
        fetchSalaryStatus.value = undefined;
      }
    }
  };

  return {
    fetchMsg,
    fetchSalarySummary,
    fetchSalaryStatus,
    fetchMonthlySalary
  }
};

export const useRegisterSalary = () => {
  const registerMsg = ref<string>('');
  const selectedMonth = ref<string>(getThisMonth());
  const registerStatusCode = ref<number>();

  const registerSalary = async (salary: number) => {
    try {
      const year = Number(selectedMonth.value.split("-")[0]);
      const month = Number(selectedMonth.value.split("-")[1]);
      const res = await postSalary(year, month, Number(salary));
      registerStatusCode.value = res.status
      if (res.status === 201) {
        registerMsg.value = year + "-" + month + "の月収:" + salary + "万円"
      }
    } catch (error: unknown) {
      registerMsg.value = parseError(error, "月収の登録に失敗しました");
      if (axios.isAxiosError(error)) {
        registerStatusCode.value = error.response?.status ?? undefined;
      } else {
        registerStatusCode.value = undefined;
      }
    }
  };

  return {
    registerMsg,
    selectedMonth,
    registerStatusCode,
    registerSalary,
  };
};
