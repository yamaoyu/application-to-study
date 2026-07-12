const errorMessages = {
  "NOT_AUTHORIZED": "認証に失敗しました",
  "INVALID_CURRENT_PASSWORD": "現在のパスワードに誤りがあります",
  "SALARY_NOT_FOUND": "月収が登録されていません",
  "USER_NOT_FOUND": "ユーザーが見つかりません",
  "SALARY_ALREADY_EXISTS": "その月の月収は既に登録されています",
  "USER_ALREADY_EXISTS": "既に登録されているユーザーです",
  "UNEXPECTED_ERROR": "予期せぬエラーが発生しました",
  "BULK_ACTIVITY_OPERATION_FAILED": "一部/全ての活動登録に失敗しました",
  "ACTIVITY_NOT_FOUND": "活動は登録されていません",
  "TODO_NOT_FOUND": "登録されたTODOはありません",
  "TODO_ALREADY_FINISHED": "既に完了したTODOです",
  "INQUIRY_NOT_FOUND": "問い合わせはありません",
  "NOT_HAVE_PERMISSION": "権限がありません",
  "INVALID_CATEGORY": "カテゴリは要望・エラー報告・その他から選択してください",
  "LOGIN_FAILED": "ユーザー名またはパスワードが正しくありません"
}

const fieldErrorMessages = {
  "INVALID_YEAR": "年は2024~2099の範囲で入力してください",
  "INVALID_MONTH": "月は1~12の範囲で入力してください",
  "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED": "月を指定する場合は年が必須です",
  "INVALID_VALUE": "不明なバリデーションエラーが発生しました",
  "EMPTY_LIST": "必要な値を指定してください"
}

export const parseError = (error, message) => {
  if (error.response) {
    switch (error.response.status) {
      case 500:
        return message;
    }

    const code = error.response.data?.code ?? error.response.code;
    if (code && code === "VALIDATION_ERROR") {
      const validationErrorCode = error.response.data.errors[0].code;
      return fieldErrorMessages[validationErrorCode] || "不明なバリデーションエラーが発生しました";
    }
    if (!code) {
      return message;
    }

    // 一括活動登録の場合は日付ごとのメッセージを作成する
    if (code==="BULK_ACTIVITY_OPERATION_FAILED") {
      const results = error.response.data.results;
      const errorMessagesList = results.map(result => {
        if (result.result === "error") {
          const reason = result.reason || "UNEXPECTED_ERROR";
          const errorMessageFn = errorMessages[reason] || errorMessages.UNEXPECTED_ERROR;
          return `${result.date}の活動登録に失敗: ${errorMessageFn}`;
        } else {
          return `${result.date}の活動登録に成功`;
        }
      });
      return errorMessagesList.join("\n");
    } else {
      return errorMessages[code];
    }

    return message;
  };

  if (error.request) {
    return "リクエストがサーバーに到達できませんでした";
  };

  return "不明なエラーが発生しました";
};
