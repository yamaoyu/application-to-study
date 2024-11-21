export function generateDropdownOptions(min, max, step) {
    const options = [];
    for (let value = min; value <= max; value += step) {
      options.push(value.toFixed(1)); // 小数点1位まで表示
    }
    return options;
}