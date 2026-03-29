import axios from 'axios';
import { backendUrl } from '../config/env';
import { useAuthStore } from '@/store/authenticate';
import { verifyRefreshToken } from './auth';
import { jwtDecode } from 'jwt-decode';

export const apiClient = axios.create({
  baseURL: backendUrl
});

apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();

  if (config.url.includes('/token')) {
    return config
  };

  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  };

  return config;
});

apiClient.interceptors.response.use(
  res => res,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const tokenResponse = await verifyRefreshToken();
        const authStore = useAuthStore();
        await authStore.setAuthData(
          tokenResponse.data.access_token,
          tokenResponse.data.token_type,
          jwtDecode(tokenResponse.data.access_token).exp
        );
        originalRequest.headers.Authorization = authStore.getAuthHeader;
        return apiClient(originalRequest);
      } catch(error) {
        return Promise.reject(error);
      }
    }
    return Promise.reject(error)
  }
);
