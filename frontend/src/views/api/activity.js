import { apiClient } from './client';

export const getActivitiesByStatus = (status) => {
  return apiClient.get(
    `activities?status=${status}`
  )
};

export const getActivityByDay = (year, month, day) => {
  return apiClient.get(
    `activities/${year}/${month}/${day}`
  )
};

export const registerTargets = (activities) => {
  return apiClient.post(
    "activities/multi/target",
    { activities }
  )
};

export const registerActuals = (activities) => {
  return apiClient.put(
    "activities/multi/actual",
    { activities }
  )
};

export const finishActivies = (dates) => {
  return apiClient.put(
    "activities/multi/finish",
    { dates }
  )
};
