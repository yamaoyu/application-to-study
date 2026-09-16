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
    "LOGIN_FAILED": "ユーザー名またはパスワードが正しくありません",
    // bulk処理でresultsに入るエラーコード
    "INVALID_TODO_TITLE": "タイトルは32文字以下としてください",
    "INVALID_TODO_DUE": "不正な日付です",
    "INVALID_TODO_DETAIL": "詳細は200文字以下としてください",
    "INVALID_TARGET_TIME": "目標時間は0.5時間以上12時間以下かつ0.5時間刻みとしてください",
    "INVALID_ACTUAL_TIME": "活動時間は12時間以下かつ0.5時間刻みとしてください"
} as const;

export const fieldErrorMessages = {
    "INVALID_YEAR": "年は2024~2099の範囲で入力してください",
    "INVALID_MONTH": "月は1~12の範囲で入力してください",
    "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED": "月を指定する場合は年が必須です",
    "INVALID_VALUE": "不明なバリデーションエラーが発生しました",
    "EMPTY_LIST": "必要な値を指定してください",
    "INVALID_PASSWORD": "パスワードは大文字、小文字、数字、記号を含めた8-16文字としてください",
    "INVALID_USERNAME": "ユーザー名は3文字以上、16文字以下としてください",
    "VACANT_ACTIVITIES": "登録する活動が指定されていません",
    "INVALID_DATES": "不正な日付が含まれるか日付が指定されていません",
    "INQUIRY_DETAIL_TOO_LONG": "詳細は256文字以下としてください",
    "INQUIRY_DETAIL_REQUIRED": "詳細は必須です",
    "INVALID_MONTHLY_INCOME": "月収は5以上2000以下としてください"
} as const;

export type ErrorCode = keyof typeof errorMessages;
export type FieldErrorCode = keyof typeof fieldErrorMessages;
