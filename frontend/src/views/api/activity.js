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

export const getActivitiesByMonth = (year, month) => {
  return apiClient.get(
    `activities/${year}/${month}`
  )
};

export const getActivitiesByYear = (year) => {
  return apiClient.get(
    `activities/${year}`
  )
};

export const getAllActivities = () => {
  return apiClient.get(
    "activities/total"
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
