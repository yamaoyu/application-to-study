import { apiClient } from './client';
import {
  SendTargetActivityParam,
  SendActualActivityParam,
  SendFinishActivityParam,
  RegisterTargetResponse,
  RegisterActualResponse,
  FinishActivityResponse,
  GetOneActivityResponse
} from '../types/activity';
import type { AxiosResponse } from "axios";

type Status =
  | "pending"
  | "success"
  | "failure"

export const getActivitiesByStatus = (status: Status) => {
  return apiClient.get(
    `activities?status=${status}`
  )
};

export const getActivityByDay = (
  year: number, month: number, day: number
): Promise<GetOneActivityResponse> => {
  return apiClient.get(
    `activities/${year}/${month}/${day}`
  )
};

export const getActivitiesByMonth = (year: number, month: number) => {
  return apiClient.get(
    `activities/${year}/${month}`
  )
};

export const getActivitiesByYear = (year: number) => {
  return apiClient.get(
    `activities/${year}`
  )
};

export const getAllActivities = () => {
  return apiClient.get(
    "activities/total"
  )
};

export const registerTargets = (
  activities: SendTargetActivityParam[]
): Promise<AxiosResponse<RegisterTargetResponse>> => {
  return apiClient.post(
    "activities/target",
    { activities }
  )
};

export const registerActuals = (
  activities: SendActualActivityParam[]
): Promise<AxiosResponse<RegisterActualResponse>> => {
  return apiClient.put(
    "activities/actual",
    { activities }
  )
};

export const finishActivies = (
  dates: SendFinishActivityParam
): Promise<AxiosResponse<FinishActivityResponse>> => {
  return apiClient.put(
    "activities/finish",
    { dates }
  )
};
