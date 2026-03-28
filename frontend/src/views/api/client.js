import axios from 'axios';
import { backendUrl } from '../config/env';
import { useAuthStore } from '@/store/authenticate';

export const apiClient = axios.create({
  baseURL: backendUrl
});

apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();

  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  };

  return config;
});
