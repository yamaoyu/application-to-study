import { ref } from 'vue';
import { registerInquiry } from '../api/inquiry';
import { parseError } from '../utils/error';

export const useSendInquiry = () => {
  const category = ref("");
  const detail = ref("");
  const statusCode = ref(null);
  const message = ref("");

  const sendRequest = async() => {
    try {
      const res = await registerInquiry(category.value, detail.value);
      if (res.status===201){
        statusCode.value = res.status
        message.value = ["以下の内容で受け付けました\n",
                        `カテゴリ:${res.data.category}\n`,
                        `内容:${res.data.detail}`].join('');
        // 内容をリセット
        category.value = "";
        detail.value = "";
      }
    } catch(error) {
      message.value = parseError(error, "問い合わせの送信処理に失敗しました");
      statusCode.value = error.response?.status ?? null;
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
