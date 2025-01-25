export function generateTimeOptions(min, max, step) {
    const timeOptions = [];
    for (let value = min; value <= max; value += step) {
      timeOptions.push(value.toFixed(1)); // 小数点1位まで表示
    }
    return timeOptions;
}

export function changeTime(time, timeOptions) {
  const increaseHalfHour = async() => {
    const currentIndex = timeOptions.indexOf(time.value)
    if (currentIndex < timeOptions.length - 1) {
      time.value = timeOptions[currentIndex + 1]
    }
  }

  const decreaseHalfHour = async() => {
    const currentIndex = timeOptions.indexOf(time.value)
    if (currentIndex > 0) {
      time.value = timeOptions[currentIndex - 1]
    }
  }

  return {
    increaseHalfHour,
    decreaseHalfHour
  }
}