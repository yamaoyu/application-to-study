import { ref } from 'vue';
import { registerInquiry, getInquiries } from '../api/inquiry';
import { parseError } from '../utils/error';
import { InquiryCategoryType, InquiryItem, DEFAULT_INQUIRY_CATEGORY } from '../types/inquiry';
import axios from 'axios';

export const useSendInquiry = () => {
  const category = ref<InquiryCategoryType>(DEFAULT_INQUIRY_CATEGORY); // 初期値は要望
  const detail = ref<string>("");
  const statusCode = ref<number | null>(null);
  const message = ref<string>("");

  const sendRequest = async () => {
    try {
      const res = await registerInquiry(category.value, detail.value);
      if (res.status === 201) {
        statusCode.value = res.status
        message.value = ["以下の内容で受け付けました\n",
          `カテゴリ:${res.data.category}\n`,
          `内容:${res.data.detail}`].join('');
        // 内容をリセット
        category.value = DEFAULT_INQUIRY_CATEGORY;
        detail.value = "";
      }
    } catch (error) {
      message.value = parseError(error, "問い合わせの送信処理に失敗しました");
      if (axios.isAxiosError(error)) {
        statusCode.value = error.response?.status ?? null;
      } else {
        statusCode.value = null;
      }
    }
  }

  return {
    category,
    detail,
    statusCode,
    message,
    sendRequest
  }
};

export const useGetInquiries = () => {
  const inquiries = ref<InquiryItem[]>([]);
  const message = ref<string>("");

  const fetchInquiries = async () => {
    try {
      const res = await getInquiries();
      inquiries.value = res.data.inquiries;
      message.value = "";
    } catch (error) {
      message.value = parseError(error, "問い合わせの取得に失敗しました");
    }
  }

  return {
    inquiries,
    message,
    fetchInquiries
  }
};
