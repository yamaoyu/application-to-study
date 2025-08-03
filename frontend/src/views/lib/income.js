import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { verifyRefreshToken, commonError } from './index';
import { jwtDecode } from 'jwt-decode';

export function getIncomeByMonth(incomeRes, incomeMsg, year, month) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(incomeMsg, router);

    const sendGetIncomeRequest = async() =>{
        const income_url = process.env.VUE_APP_BACKEND_URL + 'incomes/' + year + '/' + month;
        incomeRes.value = await axios.get(income_url,
                                        {headers: {Authorization: authStore.getAuthHeader}}
        );
        if(incomeRes.value.status===200){
            incomeMsg.value = ""
        }
    }

    const getMonthlyIncome = async() =>{
        try {
            await sendGetIncomeRequest();
        } catch(error) {
            if (error.response?.status === 401) {
                try {
                    // リフレッシュトークンを検証して新しいアクセストークンを取得
                    const tokenResponse = await verifyRefreshToken();
                    // 新しいアクセストークンをストアに保存
                    await authStore.setAuthData(
                    tokenResponse.data.access_token,
                    tokenResponse.data.token_type,
                    jwtDecode(tokenResponse.data.access_token).exp)
                    // 再度リクエストを送信
                    await sendGetIncomeRequest();
                } catch (refreshError) {
                    router.push({
                    path: "/login",
                    query: { message: "再度ログインしてください" }
                    });
                }            
            } else {
                handleError(error)
            }
        }
    }

    return getMonthlyIncome
}