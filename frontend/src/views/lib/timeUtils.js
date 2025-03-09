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