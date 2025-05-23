export function errorWithStatusCode(statusCode, message, router){
    /**
     * APIリクエストのステータス番号のリセットが必要な場合
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

export function errorWithActivityStatus(activityStatus, message, router){
    /**
     * activityStatus(未確定、未達成、達成)のリセットが必要な場合
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

export function errorWithActivity(activityRes, checkMsg, router){
    /**
     * activityRes(1日の活動記録)のリセットが必要な場合
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
            default:
                checkMsg.value = error.response.data.detail;
            }
            }
        }
    
    return {
        handleError
    }
}

export function errorWithActivities(response, activities, message, router){
    /**
     * activities(複数の活動記録)のリセットが必要な場合
     */
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

export function commonError(message, router){
    /**
     * エラー処理のみで変数の初期化をしない
     */
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
                default:
                    message.value = error.response.data.detail;
                }
            } else if (error.request){
                message.value =  "リクエストがサーバーに到達できませんでした"
            } else {
                message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
        }
        return message.value
    }

    return {
        handleError
    }
}