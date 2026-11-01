import { apiClient } from './client';
import {
    GetUsersResponse,
    GetUsersParams,
    ChangeRoleResponse,
    ChangeRoleParams,
    ChangeStatusResponse,
    ChangeStatusParams,
    ResetPasswordResponse
} from '../types/admin';
import type { AxiosResponse } from "axios";

export const getUsersList = (
    params: GetUsersParams
): Promise<AxiosResponse<GetUsersResponse>> => {
    return apiClient.get("admin/users", { params });
};

export const changeUserRole = (
    params: ChangeRoleParams
): Promise<AxiosResponse<ChangeRoleResponse>> => {
    const encodedUsername = encodeURIComponent(params.username)
    return apiClient.patch(`admin/users/${encodedUsername}/role`, { role: params.role });
};

export const changeUserStatus = (
    params: ChangeStatusParams
): Promise<AxiosResponse<ChangeStatusResponse>> => {
    const encodedUsername = encodeURIComponent(params.username)
    return apiClient.patch(`admin/users/${encodedUsername}/status`, { status: params.status });
};

export const resetUserPassword = (username: string): Promise<AxiosResponse<ResetPasswordResponse>> => {
    const encodedUsername = encodeURIComponent(username)
    return apiClient.patch(`/admin/users/${encodedUsername}/password`)
}
