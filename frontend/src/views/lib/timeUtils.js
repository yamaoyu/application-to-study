import axios from 'axios';

const BACKEND_URL = process.env.VUE_APP_BACKEND_URL;

export function generateTimeOptions(min, max, step) {
    const timeOptions = [];
    for (let value = min; value <= max; value += step) {
      timeOptions.push(value.toFixed(1)); // 小数点1位まで表示
    }
    return timeOptions;
}

export function changeTime(time) {
  const increaseHour = async(step) => {
    if ((time.value + step) <= 12) {
      time.value += step
    } else {
      time.value = 12
    }
  }

  const decreaseHour = async(step) => {
    if ((time.value - step) >= 0) {
      time.value -= step
    } else {
      time.value = 0
    }
  }

  return {
    increaseHour,
    decreaseHour
  }
}

export function useActivityFinish(date, message, router, authStore) {
  const finishActivity = async() =>{
      try {
        // 日付から年月日を取得
        const dateParts = date.value.split('-');
        const year = dateParts[0];
        // 月と日が一桁の場合、表記を変更 例)09→9
        const month = parseInt(dateParts[1], 10);
        const day = parseInt(dateParts[2], 10);
        const url = BACKEND_URL + 'activities/' + year + '/' + month + '/' + day + '/finish';
        // axiosのputの第二引数はリクエストボディとなるため{}を用意する。(リクエストボディで渡すデータはないため空)
        const response = await axios.put(url,
                                        {},
                                        {headers: {Authorization: authStore.getAuthHeader}})
        if (response.status===200){
          message.value = response.data.message
        }
      } catch (error) {
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
            message.value =  "活動の確定に失敗しました"
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
    }
  return {
      finishActivity
    }
  }