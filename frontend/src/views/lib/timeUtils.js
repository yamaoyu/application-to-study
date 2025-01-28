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