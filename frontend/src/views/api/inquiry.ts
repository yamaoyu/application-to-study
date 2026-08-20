import { apiClient } from './client';
import { InquiryCategoryType, CreateInquiryResponse, GetInquiryInfo } from '../types/inquiry';

export const registerInquiry = (category: InquiryCategoryType, detail: string) => {
  return apiClient.post<CreateInquiryResponse>(
    "inquiries",
    { category: category, detail: detail }
  )
};

export const getInquiries = () => {
  return apiClient.get<GetInquiryInfo>(
    "inquiries"
  )
};
