import { apiClient } from './client';
import { GetUsersResponse, GetUsersParams } from '../types/admin';
import type { AxiosResponse } from "axios";

export const getUsersList = (
    params: GetUsersParams
): Promise<AxiosResponse<GetUsersResponse>> => {
    return apiClient.get("admin/users", { params });
};

