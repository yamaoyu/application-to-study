import axios from 'axios';
import { backendUrl } from '../config/env';
import { useAuthStore } from '@/store/authenticate';
import { verifyRefreshToken } from './auth';
import { setAuthDataFromToken } from '../composables/useAuth';

export const apiClient = axios.create({
  baseURL: backendUrl
});

apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  const url = config.url;

  if (!url) {
    return config
  }

  if (
    url.includes('token') ||
    url.includes('users') ||
    url.includes('login')
  ) {
    return config;
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
    const url = originalRequest?.url ?? '';

    if (
      url.includes('token') ||
      url.includes('users') ||
      url.includes('login')
    ) {
      return Promise.reject(error);
    };
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const tokenResponse = await verifyRefreshToken();
        const authStore = useAuthStore();
        await setAuthDataFromToken(authStore, tokenResponse.data)
        originalRequest.headers.Authorization = authStore.getAuthHeader;
        return apiClient(originalRequest);
      } catch (error) {
        return Promise.reject(error);
      }
    }
    return Promise.reject(error)
  }
);
