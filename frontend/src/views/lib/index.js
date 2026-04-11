import { getStatusColors, getAdjustmentColors, getActivityAlert, getResponseAlert } from "./bootstrapClass";
import { verifyRefreshToken } from "./token";
import { errorWithStatusCode, errorWithActivityStatus, errorWithActivity, errorWithActivities, commonError } from "./error";
import { 
    updateActivity, registerTarget, registerActual, registerMultiTarget, registerMultiActual, 
    finalizeActivity, finalizeMultiActivities,
    getActivityByDay, getActivityByMonth, getActivityByYear, getActivitiesAllPeriod, getActivitiesByStatus } from "./activity";
import { getIncomeByMonth, registerMonthlyIncome } from "./income";
import { backendUrl } from "./baseUrl";

export {
    getStatusColors,
    getAdjustmentColors,
    getActivityAlert,
    getResponseAlert,
    verifyRefreshToken,
    errorWithStatusCode,
    errorWithActivityStatus,
    errorWithActivity,
    errorWithActivities,
    commonError,
    updateActivity,
    registerTarget,
    registerActual,
    registerMultiTarget,
    registerMultiActual,
    finalizeActivity,
    finalizeMultiActivities,
    getActivityByDay,
    getActivityByMonth,
    getActivityByYear,
    getActivitiesAllPeriod,
    getActivitiesByStatus,
    getIncomeByMonth,
    registerMonthlyIncome,
    backendUrl
}