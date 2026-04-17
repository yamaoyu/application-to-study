import { apiClient } from './client';

export const registerInquiry = (category, detail) => {
  return apiClient.post(
    "inquiries",
    { category: category, detail: detail }
  )
};

export const getInquiries = () => {
  return apiClient.get(
    "inquiries"
  )
};
