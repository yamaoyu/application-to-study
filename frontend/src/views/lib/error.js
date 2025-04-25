export function commonError(statusCode, message, router){
    /**
     * 最も多いパターンのエラー処理
     * ステータスコードを処理する必要がある場合は、この関数を呼び出す
     */
    const handleError = async(error) => {
        statusCode.value = null;
        if (error.response){
        switch (error.response.status){
            case 401:
            router.push(
                {"path":"/login",
                "query":{message:"再度ログインしてください"}
                })
                break;
            case 500:
                message.value =  "活動時間の登録に失敗しました"
                break;
            default:
                message.value = error.response.data.detail;}
            } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
            } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
            }
        }
    
    return {
        handleError
    }
}

export function finishActivityError(activityStatus, message, router){
    /**
     * 活動終了時のエラー処理
     * アクティビティステータスを使用する場合は、この関数を呼び出す
     */
    const handleError = async(error) => {
        activityStatus.value = null;
        if (error.response){
        switch (error.response.status){
            case 401:
            router.push(
                {"path":"/login",
                "query":{message:"再度ログインしてください"}
                })
                break;
            case 500:
                message.value =  "活動終了に失敗しました"
                break;
            default:
                message.value = error.response.data.detail;}
            } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
            } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
            }
        }

    return {
        handleError
    }
}

export function getActivityError(activityRes, checkMsg, router){
    /**
     *
     */
    const handleError = async(error) =>{
        activityRes.value = ""
        if (error.response){
            switch (error.response.status){
            case 401:
            router.push(
                {"path":"/login",
                "query":{message:"再度ログインしてください"}
                })
                break;
            case 422:
                checkMsg.value = error.response.data.detail;
                break;
            case 500:
                checkMsg.value =  "活動の取得に失敗しました"
                break;
            default:
                checkMsg.value = error.response.data.detail;
            }
            }
        }
    
    return {
        handleError
    }
}

export function getMonthlyinfoError(response, activities, message, router){
    const handleError = async(error) =>{
        response.value = null
        activities.value = []
        if (error.response){
            switch (error.response.status){
            case 401:
                router.push(
                {"path":"/login",
                 "query":{message:"再度ログインしてください"}
                })
                break;
            case 500:
                message.value =  "情報の取得に失敗しました"
                break;
            default:
                message.value = error.response.data.detail;}
        } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
        } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
        }
    }
    return {
        handleError
    }
}

export function allActivitiesError(message, router){
    const handleError = async(error) =>{
        if (error.response){
            switch (error.response.status){
                case 401:
                    router.push(
                        {"path":"/login",
                        "query":{message:"再度ログインしてください"}
                    })
                    break;
                case 422:
                    message.value = error.response.data.detail;
                    break;
                case 500:
                    message.value =  "情報の取得に失敗しました"
                    break;
                default:
                    message.value = error.response.data.detail;
                }
            } else if (error.request){
                message.value =  "リクエストがサーバーに到達できませんでした"
            } else {
                message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
        }
    }

    return {
        handleError
    }
}