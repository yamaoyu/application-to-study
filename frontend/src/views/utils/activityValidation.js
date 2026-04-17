export const validateTargetTime = (time) => {
  if (time === null || time === undefined) {
    return "時間を入力してください";
  }

  if (time < 0.5) {
    return "時間は0.5時間以上入力してください";
  }

  if (time * 2 % 1 !== 0) {
    return "時間は0.5時間単位で入力してください";
  }

  return null
};

export const hasDuplicateDate = (dates, date) => {
  return dates.filter(d=>d && d===date).length > 1;
};

export const isValidActivities = (activities) => {
  return !activities.some(a => !a.date || !a.target_time)
};

export const validateActualTime = (time) => {
  if (time === null || time === undefined) {
    return "時間を入力してください";
  }

  if (time * 2 % 1 !== 0) {
    return "時間は0.5時間単位で入力してください";
  }

  return null
};
