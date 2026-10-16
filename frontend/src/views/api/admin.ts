import { apiClient } from './client';
import {
    GetUsersResponse,
    GetUsersParams,
    ChangeRoleResponse,
    ChangeRoleParams,
    ChangeStatusResponse,
    ChangeStatusParams
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
    return apiClient.patch(`admin/users/${params.username}/role`, { role: params.role });
};

export const changeUserStatus = (
    params: ChangeStatusParams
): Promise<AxiosResponse<ChangeStatusResponse>> => {
    return apiClient.patch(`admin/users/${params.username}/status`, { status: params.status });
};

