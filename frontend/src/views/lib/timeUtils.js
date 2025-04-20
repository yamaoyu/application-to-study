export function generateTimeOptions(min, max, step) {
    const timeOptions = [];
    for (let value = min; value <= max; value += step) {
      timeOptions.push(value.toFixed(1)); // 小数点1位まで表示
    }
    return timeOptions;
}