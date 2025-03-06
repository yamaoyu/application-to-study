export function commonError(statusCode, message, router){
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