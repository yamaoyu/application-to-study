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

function registerActivity(config) {
    return function(date, statusCode, time, reqMsg, checkMsg, activityRes) {
        const router = useRouter();
        const authStore = useAuthStore();
        const { renewActivity } = updateActivity(date, checkMsg, activityRes);
        const { handleError } = errorWithStatusCode(statusCode, reqMsg, router);

        const submitActivity = async() => {
            const dateParts = date.value.split('-');
            const year = dateParts[0];
            const month = parseInt(dateParts[1], 10);
            const day = parseInt(dateParts[2], 10);
            const url = `${process.env.VUE_APP_BACKEND_URL}activities/${year}/${month}/${day}/${config.endpoint}`;
            
            const response = await axios[config.method](url, 
                {[config.valueKey]: Number(time.value)},
                {headers: {Authorization: authStore.getAuthHeader}})
            
            statusCode.value = response.status;
            if (response.status === config.expectedStatus) {
                reqMsg.value = response.data.message;
            }
        }

        const register = async() => {
            try {
                await submitActivity();
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
                        await submitActivity();
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

        return { register };
    }
}

export const registerTarget = registerActivity({
    endpoint: 'target',
    method: 'post',
    valueKey: 'target_time',
    expectedStatus: 201
});

export const registerActual = registerActivity({
    endpoint: 'actual',
    method: 'put',
    valueKey: 'actual_time',
    expectedStatus: 200
});

function registerMultiActivities(config){
    return function(date, statusCode, reqMsg, activities, checkMsg, activityRes) {
        const router = useRouter();
        const authStore = useAuthStore();
        const { renewActivity } = updateActivity(date, checkMsg, activityRes);
        const { handleError } = errorWithStatusCode(statusCode, reqMsg, router);

        const submitMultiActivities = async() => {
            // 複数の活動を登録する処理
            const url = process.env.VUE_APP_BACKEND_URL + "activities/multi/" + config.endpoint;
            const response = await axios[config.method](url,
                                            {activities: activities.value},
                                            {headers: {Authorization: authStore.getAuthHeader}});
            statusCode.value = response.status;
            if (response.status===config.expectedStatus){
                reqMsg.value = response.data.message;
                }
        }

        const register = async() =>{
            // 送信ボタンを押した際に実行される処理
            try {
                await submitMultiActivities();
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
                        await submitMultiActivities();
                    } catch (refreshError) {
                        router.push({
                        path: "/login",
                        query: { message: "再度ログインしてください" }
                        });
                    }            
                } else {
                    handleError(error);
                }
            }
        
            // 結果に関わらず、活動のリストを初期値にリセット
            if (config.endpoint==="target"){
                activities.value.splice(0, activities.value.length, ...config.default.map(obj => ({ ...obj })));
            } else {
                activities.value.length = config.default;
            }
        }

        return {
            register
        }
    }
}

export const registerMultiTarget = registerMultiActivities({
    endpoint: 'target',
    method: 'post',
    expectedStatus: 201,
    default: [{ date: '', target_time: 0.5 }]
});

export const registerMultiActual = registerMultiActivities({
    endpoint: 'actual',
    method: 'put',
    expectedStatus: 200,
    default: 0
});

export function finalizeActivity(date, reqMsg, activityStatus, checkMsg, activityRes) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError: handleFinishError } = errorWithActivityStatus(activityStatus, reqMsg, router);
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
            reqMsg.value = response.data.message;
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

export function finalizeMultiActivities(date, selectedActivities, reqMsg, statusCode, checkMsg, activityRes) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { renewActivity } = updateActivity(date, checkMsg, activityRes);
    const { handleError: handleFinishError } = errorWithStatusCode(statusCode, reqMsg, router);

    const sendFinishMultiRequest = async() => {
        // 選択された活動を終了するリクエストを送信する関数
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/multi/finish';
        const response = await axios.put(url,
                                    {"dates": selectedActivities.value},
                                    {headers: {Authorization: authStore.getAuthHeader}}
                                )
        if (response.status===200){
            statusCode.value = response.status;
            let msg = '';
            if (response.data.pay_adjustment) msg += `ボーナス-ペナルティ：${response.data.pay_adjustment}\n`;
            if (response.data.total_bonus) msg += `ボーナス：${response.data.total_bonus}\n`;
            if (response.data.total_penalty) msg += `ペナルティ：${response.data.total_penalty}\n`;
            if (response.data.message) msg += response.data.message;
            reqMsg.value = msg;
            selectedActivities.value = [];
        }
    }

    const finishMultiActivities = async() =>{
        // 選択された活動を終了するボタンがクリックされたときに実行される
        try {
            await sendFinishMultiRequest();
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
                    await sendFinishMultiRequest();
                } catch (refreshError) {
                    router.push({path: "/login",
                    query: { message: "再度ログインしてください" }
                    });
                }
            } else {
                handleFinishError(error)
            }
        }
    }
    return {
            finishMultiActivities
        }
}

export function getActivityByDay(year, month, date, activityRes, activityStatus, message) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = errorWithActivityStatus(activityStatus, message, router);

    const sendRequestForDailyInfo = async() =>{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month + '/' + date;
        activityRes.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
    }

    const getDailyInfo = async() =>{
        try{
            await sendRequestForDailyInfo();
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
                    await sendRequestForDailyInfo();
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

    return getDailyInfo
}

export function getActivityByMonth(selectedMonth, response, activities, reqMsg) {
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = errorWithActivities(response, activities, reqMsg, router);

    const sendRequestForMonthlyInfo = async() =>{
        const [year, month] = selectedMonth.value.split('-').map(Number)
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year + '/' + month;
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.value.status===200){
            activities.value = response.value.data.activity_list;
            reqMsg.value = ""
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

export function getActivityByYear(year, response, activities, reqMsg){
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(reqMsg, router);

    const sendRequestForMonthlyInfo = async() =>{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/' + year.value;
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.value.status===200){
            activities.value = response.value.data.monthly_info;
            reqMsg.value = ""
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

export function getActivitiesAllPeriod(response, reqMsg){
    const router = useRouter();
    const authStore = useAuthStore();
    const { handleError } = commonError(reqMsg, router);

    const sendRequestForAllPeriod = async() =>{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/total';
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.value.status==200){
            reqMsg.value = ""
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
            pendingMsg.value = "";
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
                handleError(error);
            }
        }
    }

    return {
        getPendingActivities
    }
}