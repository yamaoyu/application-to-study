import { getStatusColors, getAdjustmentColors, getActivityAlert, getResponseAlert } from "./bootstrapClass";
import { verifyRefreshToken } from "./token";
import { errorWithStatusCode, errorWithActivityStatus, errorWithActivity, errorWithActivities, commonError } from "./error";
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
    backendUrl
}