const errorMessages = {
  "NOT_AUTHORIZED": "認証に失敗しました",
  "INVALID_CURRENT_PASSWORD": "現在のパスワードに誤りがあります",
  "SALARY_NOT_FOUND_ERROR": "月収が登録されていません",
  "USER_NOT_FOUND": "ユーザーが見つかりません",
  "SALARY_ALREADY_EXISTS": "その月の月収は既に登録されています",
  "USER_ALREADY_EXISTS": "既に登録されているユーザーです",
  "UNEXPECTED_ERROR": "予期せぬエラーが発生しました"
}

export const parseError = (error, message) => {
  if (error.response) {
    const code = error.response.data?.code ?? error.response.code;
    if (code && errorMessages[code]) {
      return errorMessages[code];
    }

    switch (error.response.status) {
      case 500:
        return message;
      default:
        return error.response.data.detail;
    }
  };

  if (error.request) {
    return "リクエストがサーバーに到達できませんでした";
  };

  return "不明なエラーが発生しました";
};
