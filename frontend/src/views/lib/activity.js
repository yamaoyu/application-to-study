import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { verifyRefreshToken, errorWithActivity, errorWithStatusCode, errorWithActivityStatus, errorWithActivities, commonError } from './index';
import { jwtDecode } from 'jwt-decode';


export function updateActivity(date, checkMsg, activityRes) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError: handleActivityError } = errorWithActivity(activityRes, checkMsg, router);

    const getActivity = async() => {
        // 活動情報を取得リクエストを送信する関数
        const dateParts = date.value.split('-');
        const year = dateParts[0];
        let month = dateParts[1];
        let day = dateParts[2];
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day;
        activityRes.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        checkMsg.value = ""
    }

    const renewActivity = async() =>{
        // 日付が変更された時と終了ボタンがクリックされた時に実行される
        try {
            await getActivity();
        } catch (error) {
            if (error.response?.status === 401) {
            // リフレッシュトークンを検証して新しいアクセストークンを取得
            try {
                const tokenResponse = await verifyRefreshToken();
                await authStore.setAuthData(
                tokenResponse.data.access_token,
                tokenResponse.data.token_type,
                jwtDecode(tokenResponse.data.access_token).exp)
                // 再度リクエストを送信
                await getActivity();
            } catch (refreshError) {
                router.push({
                path: "/login",
                query: { message: "再度ログインしてください" }
                });
            }            
            } else {
                handleActivityError(error)
            }
        }
    }

    return {
        renewActivity,
    }
}

export function registerActivity(date, statusCode, targetTime, actualTime, message, checkMsg, activityRes) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { renewActivity } = updateActivity(date, checkMsg, activityRes);
    const { handleError } = errorWithStatusCode(statusCode, message, router);

    const submitTarget = async() =>{
        // 目標時間を送信する処理
        const dateParts = date.value.split('-');
        const year = dateParts[0];
        // 月と日が一桁の場合、表記を変更 例)09→9
        const month = parseInt(dateParts[1], 10);
        const day = parseInt(dateParts[2], 10);
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day + '/target';
        const response = await axios.post(url, 
                                        {target_time: Number(targetTime.value)},
                                        {headers: {Authorization: authStore.getAuthHeader}})
        statusCode.value = response.status
        if (response.status===201){
            message.value = response.data.message
            }
        }
    
    const registerTarget = async() =>{
        // 登録ボタンクリック時に実行される関数
        try {
            await submitTarget();
            // 更新後の活動情報を取得
            await renewActivity();
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
            await submitTarget();
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

    const submitActual = async() =>{
        // 目標時間を登録する処理
        const dateParts = date.value.split('-');
        const year = dateParts[0];
        // 月と日が一桁の場合、表記を変更 例)09→9
        const month = parseInt(dateParts[1], 10);
        const day = parseInt(dateParts[2], 10);
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day +  '/actual';
        const response = await axios.put(url, 
                                        {actual_time: Number(actualTime.value)},
                                        {headers: {Authorization: authStore.getAuthHeader}})
        statusCode.value = response.status
        if (response.status===200){
            message.value = response.data.message
            }
        }
    
    const registerActual = async() =>{
        // 登録ボタンクリック時に実行される関数
        try {
            await submitActual();
            // 更新後の活動情報を取得
            await renewActivity();
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
            await submitActual();
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

    return {
        registerTarget,
        registerActual,
    }
}

export function finalizeActivity(date, finMsg, activityStatus, checkMsg, activityRes) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError: handleFinishError } = errorWithActivityStatus(activityStatus, finMsg, router);
    const { renewActivity } = updateActivity(date, checkMsg, activityRes);

    const sendFinishRequest = async() => {
        // 活動終了リクエストを送信する関数 
        const dateParts = date.value.split('-');
        const year = dateParts[0];
        const month = parseInt(dateParts[1], 10);
        const day = parseInt(dateParts[2], 10);
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + day + '/finish';
        // axiosのputの第二引数はリクエストボディとなるため{}を用意する。(リクエストボディで渡すデータはないため空)
        const response = await axios.put(url,
                                        {},
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.status===200){
            activityStatus.value = response.data.status;
            finMsg.value = response.data.message;
        }
    }

    const finishActivity = async() =>{
    // 活動終了ボタンがクリックされたときに実行される
    try {
        await sendFinishRequest();
        // 更新後の活動情報を取得
        await renewActivity();
    } catch (error) {
        if (error.response?.status === 401) {
        // リフレッシュトークンを検証して新しいアクセストークンを取得
        try {
            const tokenResponse = await verifyRefreshToken();
            await authStore.setAuthData(
            tokenResponse.data.access_token,
            tokenResponse.data.token_type,
            jwtDecode(tokenResponse.data.access_token).exp)
            // 再度リクエストを送信
            await sendFinishRequest();
        } catch (refreshError) {
            router.push({
            path: "/login",
            query: { message: "再度ログインしてください" }
            });
        }            
        } else {
            handleFinishError(error)
        }
    }
    }

    return {
        finishActivity
    }
}

export function getActivityByMonth(selectedMonth, response, activities, message) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = errorWithActivities(response, activities, message, router);

    const sendRequestForMonthlyInfo = async() =>{
        const [year, month] = selectedMonth.value.split('-').map(Number)
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month;
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.value.status===200){
            activities.value = response.value.data.activity_list;
            message.value = ""
        } 
    }

    const getMonthlyInfo = async() =>{
        // 検索ボタンが押された時の処理
        try{
            await sendRequestForMonthlyInfo();
        } catch (error){
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
                    await sendRequestForMonthlyInfo();
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

    return {
        getMonthlyInfo
    }
}

export function getActivityByYear(year, response, activities, message){
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(message, router);

    const sendRequestForMonthlyInfo = async() =>{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value;
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.value.status===200){
            activities.value = response.value.data.monthly_info;
            message.value = ""
            } 
        }
    
    const getYearlyInfo = async() =>{
        // 検索ボタンが押された時の処理
        try{
        await sendRequestForMonthlyInfo();
        } catch (error){
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
            await sendRequestForMonthlyInfo();
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

    return {
        getYearlyInfo
    }
}

export function getActivitiesAllPeriod(response, message){
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(message, router);

    const sendRequestForAllPeriod = async() =>{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/total';
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.value.status==200){
            message.value = ""
        }
    }

    const getAllActivities = async() =>{
        try{
            await sendRequestForAllPeriod()
        } catch (error){
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
                    await sendRequestForAllPeriod();
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

    return {
        getAllActivities
    }

}

export function getActivitiesByStatus(pendingActivities, pendingMsg){
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(pendingMsg, router);

    const sendPendingRequest = async() =>{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities?status=pending';
        const response = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.status==200){
            pendingActivities.value = response.data.activities;
            pendingMsg.value = ""
        }
    }

    const getPendingActivities = async() =>{
        try{
            await sendPendingRequest()
        } catch(error){
            pendingActivities.value = []
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
                    await sendPendingRequest();
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

    return {
        getPendingActivities
    }
}