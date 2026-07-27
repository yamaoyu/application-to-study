export const errorMessages = {
    "NOT_AUTHORIZED": "認証に失敗しました",
    "INVALID_CURRENT_PASSWORD": "現在のパスワードに誤りがあります",
    "SALARY_NOT_FOUND": "月収が登録されていません",
    "USER_NOT_FOUND": "ユーザーが見つかりません",
    "SALARY_ALREADY_EXISTS": "その月の月収は既に登録されています",
    "USER_ALREADY_EXISTS": "既に登録されているユーザーです",
    "UNEXPECTED_ERROR": "予期せぬエラーが発生しました",
    "BULK_ACTIVITY_OPERATION_FAILED": "一部/全ての活動登録に失敗しました",
    "TARGET_TIME_ALREADY_REGISTERED": "既に登録されています",
    "ACTIVITY_NOT_FOUND": "活動が登録されていません",
    "ACTIVITY_ALREADY_FINISHED": "既に確定されています",
    "TODO_NOT_FOUND": "登録されたTODOはありません",
    "TODO_ALREADY_FINISHED": "既に完了したTODOです",
    "INQUIRY_NOT_FOUND": "問い合わせはありません",
    "NOT_HAVE_PERMISSION": "権限がありません",
    "INVALID_CATEGORY": "カテゴリは要望・エラー報告・その他から選択してください",
    "LOGIN_FAILED": "ユーザー名またはパスワードが正しくありません"
} as const;

export const fieldErrorMessages = {
    "INVALID_YEAR": "年は2024~2099の範囲で入力してください",
    "INVALID_MONTH": "月は1~12の範囲で入力してください",
    "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED": "月を指定する場合は年が必須です",
    "INVALID_VALUE": "不明なバリデーションエラーが発生しました",
    "EMPTY_LIST": "必要な値を指定してください"
} as const;

export type ErrorCode = keyof typeof errorMessages;
export type FieldErrorCode = keyof typeof fieldErrorMessages;
