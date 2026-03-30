import { ref } from "vue";
import { getMonthlySalary, postSalary } from "../api/salary";
import { getThisMonth } from "../utils/date";
import { parseError } from "../utils/error";

export const useMonthlyFetchSalary = () => {
  const fetchMsg = ref('');
  const fetchRes = ref(null);

  const fetchMonthlySalary = async(year, month) => {
    try {
      const res = await getMonthlySalary(year, month);
      if(res.status===200){
        fetchMsg.value = "";
      } 
      fetchRes.value = res;
    } catch (error) {
      fetchMsg.value = parseError(error, "月収の取得に失敗しました");
      fetchRes.value = error.response ?? null;
    }
  };

  return {
    fetchMsg,
    fetchRes,
    fetchMonthlySalary
  }
};

export const useRegisterSalary = () => {
  const registerMsg = ref('');
  const selectedMonth = ref(getThisMonth());
  const registerStatusCode = ref(null);

  const registerSalary = async(salary) => {
    try {
      const year = selectedMonth.value.split("-")[0];
      const month = selectedMonth.value.split("-")[1];
      const res = await postSalary(year, month, Number(salary));
      registerStatusCode.value = res.status
      if (res.status===201){
          registerMsg.value = res.data.message
      }
    } catch (error) {
      registerMsg.value = parseError(error, "月収の登録に失敗しました");
      registerStatusCode.value = error.response?.status ?? null;
    }
  };

  return {
    registerMsg,
    selectedMonth,
    registerStatusCode,
    registerSalary,
  };
};
