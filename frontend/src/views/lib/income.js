import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { verifyRefreshToken, commonError, errorWithStatusCode } from './index';
import { jwtDecode } from 'jwt-decode';

export function getIncomeByMonth(incomeRes, incomeMsg, year, month) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(incomeMsg, router);

    const sendGetIncomeRequest = async() =>{
        const income_url = import.meta.env.VITE_BACKEND_URL + 'incomes/' + year + '/' + month;
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

export function registerMonthlyIncome(selectedMonth, monthlyIncome, incomeMsg, statusCode) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = errorWithStatusCode(statusCode, incomeMsg, router);

    const submitSalary = async() =>{
        // 給料を登録する処理
        const year = selectedMonth.value.split("-")[0]
        const month = selectedMonth.value.split("-")[1]
        const url = import.meta.env.VITE_BACKEND_URL + 'incomes/'+ year + '/' + month;
        const response = await axios.post(url, 
                                            {salary: Number(monthlyIncome.value)},
                                            {headers: {Authorization: authStore.getAuthHeader}})
        statusCode.value = response.status
        if (response.status===201){
            incomeMsg.value = response.data.message
        }
    };

    const registerSalary = async() =>{
      // 登録ボタンクリック時実行される関数
        try {
            await submitSalary();
        } catch (error) {
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
                await submitSalary();
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
    };
    
    return registerSalary
}