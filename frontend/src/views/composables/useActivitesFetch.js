import { ref } from "vue";
import { getActivitiesByStatus, getActivityByDay } from "../api/activity";
import { parseError } from "../utils/error";
import { getToday } from "../utils/date";

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
