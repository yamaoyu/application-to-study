import { ref } from "vue";
import { getActivitiesByStatus, getActivityByDay, getActivitiesByMonth, getActivitiesByYear, getAllActivities } from "../api/activity";
import { parseError } from "../utils/error";
import { getToday, getThisMonth, getThisYear } from "../utils/date";

export const useFetchActivtiesByStatus = () => {
  const pendingMsg = ref("");
  const pendingActivities = ref([]);
  const pendingStatus = ref(null);

  const fetchActivitiesByStatus = async(status) =>{
    try {
      const res = await getActivitiesByStatus(status);
      if(res.status===200){
        pendingActivities.value = res.data.activities;
        pendingMsg.value = "";
      } 
      pendingStatus.value = res;
    } catch (error) {
      pendingMsg.value = parseError(error, "月収の取得に失敗しました");
    }
  }

  return {
    pendingMsg,
    pendingActivities,
    pendingStatus,
    fetchActivitiesByStatus
  }
};

export const useFetchActivtyByDay = () => {
  const date = ref(getToday());
  const checkMsg = ref("");
  const activityRes = ref(null);

  const fetchActivityByDay = async() => {
    try {
      const dateParts = date.value.split('-');
      const year = dateParts[0];
      const month = dateParts[1];
      const day = dateParts[2];
      activityRes.value = await getActivityByDay(year, month, day);
      if (activityRes.value?.status === 200) {
        const bonusInYen = parseInt(activityRes.value.data.bonus * 10000, 10);
        const penaltyInYen = parseInt(activityRes.value.data.penalty * 10000, 10);
        if (activityRes.value.data.status === "success") {
          checkMsg.value = `目標達成!\nボーナス:${activityRes.value.data.bonus}万円(${bonusInYen}円)`;
        } else if (activityRes.value.data.status === "failure") {
          checkMsg.value = `目標失敗...\nペナルティ:${activityRes.value.data.penalty}万円(${penaltyInYen}円)`;
        } else {
          if (activityRes.value.data.target_time <= activityRes.value.data.actual_time) {
            checkMsg.value = `目標達成!活動を終了してください\n確定後のボーナス:${activityRes.value.data.bonus}万円(${bonusInYen}円)`;
          } else {
            checkMsg.value = `このままだと、${activityRes.value.data.penalty}万円(${penaltyInYen}円)のペナルティが発生`;
          }
        }
      }
    } catch(error) {
      checkMsg.value = parseError(error, "活動記録の取得に失敗しました");
      activityRes.value = null;
    }
  }

  return {
    date,
    checkMsg,
    activityRes,
    fetchActivityByDay
  }
};

export const useFetchActivitiesByMonth = (response, activities, message) => {
  const selectedMonth = ref(getThisMonth());

    const fetchActivitiesByMonth = async() => {
    try {
      const [year, month] = selectedMonth.value.split('-').map(Number)
      response.value = await getActivitiesByMonth(year, month);
      if (response.value.status===200){
        activities.value = response.value.data.activity_list;
        message.value = ""
      } 
    } catch (error) {
      message.value = parseError(error, `${selectedMonth}の活動取得に失敗しました`);
      activities.value = [];
    }
  };

  return {
    selectedMonth,
    fetchActivitiesByMonth
  }
};

export const useFetchActivitiesByYear = (response, activities, message) => {
  const selectedYear = ref(getThisYear());

  const fetchActivitiesByYear = async() => {
    try {
      response.value = await getActivitiesByYear(selectedYear.value);
      if (response.value.status===200){
        activities.value = response.value.data.monthly_info;
        message.value = "";
      } 
    } catch (error) {
      message.value = parseError(error, `${selectedYear}の活動取得に失敗しました`);
      activities.value = [];
    }
  };

  return {
    selectedYear,
    fetchActivitiesByYear
  }
};

export const useFetchAllActivities = (response, message) => {
  const fetchAllActivities = async() => {
    try {
      response.value = await getAllActivities();
      if (response.value.status==200){
            message.value = ""
        }
    } catch (error) {
      message.value = parseError(error, "全期間の活動記録取得に失敗しました")
    }
  }

  return {
    fetchAllActivities
  }
};
