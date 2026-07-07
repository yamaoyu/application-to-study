const errorMessages = {
  "NOT_AUTHORIZED": "認証に失敗しました",
  "INVALID_CURRENT_PASSWORD": "現在のパスワードに誤りがあります",
  "SALARY_NOT_FOUND_ERROR": "月収が登録されていません",
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
  "INVALID_CATEGORY": "カテゴリは要望・エラー報告・その他から選択してください"
}

export const parseError = (error, message) => {
  if (error.response) {
    switch (error.response.status) {
      case 500:
        return message;
    }

    const code = error.response.data?.code ?? error.response.code;
    if (code && errorMessages[code]) {
      return errorMessages[code];
    }
  };

  if (error.request) {
    return "リクエストがサーバーに到達できませんでした";
  };

  return "不明なエラーが発生しました";
};
