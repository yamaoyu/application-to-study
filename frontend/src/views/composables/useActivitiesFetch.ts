import { ref } from "vue";
import { getActivitiesByStatus, getActivityByDay, getActivitiesByMonth, getActivitiesByYear, getAllActivities } from "../api/activity";
import { parseError } from "../utils/error";
import { getToday, getThisMonth, getThisYear } from "../utils/date";
import {
  OneActivity,
  ActivitySummary,
  MonthlyActivity,
  MonthKey,
  GetOneActivityResponse,
  YearlyMonthlyInfo,
  ActivityStatus
} from "../types/activity";


export const useFetchActivtiesByStatus = () => {
  const pendingMsg = ref<string>("");
  const pendingActivities = ref<OneActivity[]>([]);
  const pendingStatus = ref<number | null>(null);

  const fetchActivitiesByStatus = async (status: ActivityStatus) => {
    try {
      const res = await getActivitiesByStatus(status);
      pendingActivities.value = res.data.activities;
      pendingMsg.value = "";
      pendingStatus.value = res.status;
    } catch (error) {
      pendingMsg.value = parseError(error, "月収の取得に失敗しました");
      pendingActivities.value = [];
      pendingStatus.value = null;
    }
  }

  return {
    pendingMsg,
    pendingActivities,
    pendingStatus,
    fetchActivitiesByStatus
  }
};

export const useFetchActivityByDay = () => {
  const date = ref<string>(getToday());
  const checkMsg = ref<string>("");
  const activityByDay = ref<GetOneActivityResponse>();

  const fetchActivityByDay = async () => {
    try {
      const dateParts = date.value.split('-').map(Number);
      const year = dateParts[0];
      const month = dateParts[1];
      const day = dateParts[2];
      const res = await getActivityByDay(year, month, day);
      if (res.status === 200) {
        const bonusInYen = parseInt(`${res.data.bonus * 10000}`, 10);
        const penaltyInYen = parseInt(`${res.data.penalty * 10000}`, 10);
        if (res.data.status === "success") {
          checkMsg.value = `目標達成!\nボーナス:${res.data.bonus}万円(${bonusInYen}円)`;
        } else if (res.data.status === "failure") {
          checkMsg.value = `目標失敗...\nペナルティ:${res.data.penalty}万円(${penaltyInYen}円)`;
        } else {
          if (res.data.target_time <= res.data.actual_time) {
            checkMsg.value = `目標達成!活動を終了してください\n確定後のボーナス:${res.data.bonus}万円(${bonusInYen}円)`;
          } else {
            checkMsg.value = `このままだと、${res.data.penalty}万円(${penaltyInYen}円)のペナルティが発生`;
          }
        }
        activityByDay.value = res.data;
      }
    } catch (error) {
      checkMsg.value = parseError(error, "活動記録の取得に失敗しました");
      activityByDay.value = undefined;
    }
  }

  return {
    date,
    checkMsg,
    activityByDay,
    fetchActivityByDay
  }
};

export const useFetchActivitiesByMonth = () => {
  const selectedMonth = ref<string>(getThisMonth());
  const monthlyActivities = ref<MonthlyActivity[]>([]);
  const monthlyActivitiesMessage = ref<string>("");
  const monthlySummary = ref<ActivitySummary>();

  const fetchActivitiesByMonth = async () => {
    try {
      const [year, month] = selectedMonth.value.split('-').map(Number)
      const res = await getActivitiesByMonth(year, month);
      monthlyActivities.value = res.data.activity_list;
      monthlySummary.value = {
        total_income: res.data.total_income,
        salary: res.data.salary,
        pay_adjustment: res.data.pay_adjustment,
        bonus: res.data.bonus,
        penalty: res.data.penalty,
        success_days: res.data.success_days,
        fail_days: res.data.fail_days
      }
      monthlyActivitiesMessage.value = ""
    } catch (error) {
      monthlyActivitiesMessage.value = parseError(error, `${selectedMonth.value}の活動取得に失敗しました`);
      monthlyActivities.value = [];
      monthlySummary.value = undefined;
    }
  };

  return {
    selectedMonth,
    monthlyActivities,
    monthlyActivitiesMessage,
    monthlySummary,
    fetchActivitiesByMonth
  }
};

export const useFetchActivitiesByYear = () => {
  const selectedYear = ref<number>(getThisYear());
  const yearlyActivities = ref<Record<MonthKey, Partial<YearlyMonthlyInfo>>>();
  const yearlyActivitiesMessage = ref<string>("");
  const yearlySummary = ref<ActivitySummary>();

  const fetchActivitiesByYear = async () => {
    try {
      const res = await getActivitiesByYear(selectedYear.value);
      yearlyActivities.value = res.data.monthly_info;
      yearlyActivitiesMessage.value = "";
      yearlySummary.value = {
        total_income: res.data.total_income,
        salary: res.data.salary,
        pay_adjustment: res.data.pay_adjustment,
        bonus: res.data.bonus,
        penalty: res.data.penalty,
        success_days: res.data.success_days,
        fail_days: res.data.fail_days
      }
    } catch (error) {
      yearlyActivitiesMessage.value = parseError(error, `${selectedYear.value}の活動取得に失敗しました`);
      yearlyActivities.value = undefined;
      yearlySummary.value = undefined;
    }
  };

  return {
    selectedYear,
    yearlyActivities,
    yearlyActivitiesMessage,
    yearlySummary,
    fetchActivitiesByYear
  }
};

export const useFetchAllActivities = () => {
  const allActivitiesMessage = ref<string>("");
  const allActivitiesSummary = ref<ActivitySummary>();

  const fetchAllActivities = async () => {
    try {
      const res = await getAllActivities();
      if (res.status === 200) {
        allActivitiesMessage.value = "";
        allActivitiesSummary.value = {
          total_income: res.data.total_income,
          salary: res.data.salary,
          pay_adjustment: res.data.pay_adjustment,
          bonus: res.data.bonus,
          penalty: res.data.penalty,
          success_days: res.data.success_days,
          fail_days: res.data.fail_days
        }
      }
    } catch (error) {
      allActivitiesMessage.value = parseError(error, "全期間の活動記録取得に失敗しました");
      allActivitiesSummary.value = undefined;
    }
  }

  return {
    allActivitiesMessage,
    allActivitiesSummary,
    fetchAllActivities
  }
};
