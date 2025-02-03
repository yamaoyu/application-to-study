import axios from 'axios';

const BACKEDN_URL = process.env.VUE_APP_BACKEND_URL;

export function generateTimeOptions(min, max, step) {
    const timeOptions = [];
    for (let value = min; value <= max; value += step) {
      timeOptions.push(value.toFixed(1)); // 小数点1位まで表示
    }
    return timeOptions;
}

export function changeTime(time, timeOptions, message) {
  const increaseHalfHour = async() => {
    const currentIndex = timeOptions.indexOf(time.value)
    if (currentIndex < timeOptions.length - 1) {
      time.value = timeOptions[currentIndex + 1]
      message.value = ""
    } else {
      message.value = "12時間を超える時間は設定できません";
    }
  }

  const decreaseHalfHour = async() => {
    const currentIndex = timeOptions.indexOf(time.value)
    if (currentIndex > 0) {
      time.value = timeOptions[currentIndex - 1]
      message.value = "";
    } else {
      message.value = timeOptions[0] + "時間以下は設定できません";
    }
  }

  const increaseTwoHour = async() => {
    const currentIndex = timeOptions.indexOf(time.value)
    if (currentIndex < timeOptions.length - 4) {
      time.value = timeOptions[currentIndex + 4]
      message.value = "";
    } else {
      message.value = "12時間を超える時間は設定できません";
    }
  }

  const decreaseTwoHour = async() => {
    const currentIndex = timeOptions.indexOf(time.value)
    if (currentIndex > 2) {
      time.value = timeOptions[currentIndex - 4];
      message.value = "";
    } else {
      message.value = timeOptions[0] + "時間以下は設定できません";
    }
  }

  return {
    increaseHalfHour,
    decreaseHalfHour,
    increaseTwoHour,
    decreaseTwoHour
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
        const url = BACKEDN_URL + 'activities/' + year + '/' + month + '/' + day + '/finish';
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