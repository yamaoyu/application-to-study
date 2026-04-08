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
