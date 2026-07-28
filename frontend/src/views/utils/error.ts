import {
  errorMessages,
  fieldErrorMessages,
  type ErrorCode,
  type FieldErrorCode,
} from "../types/error";

const isErrorCode = (code: unknown): code is ErrorCode => {
  return typeof code === "string" && code in errorMessages;
};

const isFieldErrorCode = (code: unknown): code is FieldErrorCode => {
  return typeof code === "string" && code in fieldErrorMessages;
};

type BulkActivityResult = {
  result: "success" | "error";
  date: string;
  reason?: unknown;
};

type ErrorResponseData = {
  code?: unknown;
  errors?: { code?: unknown }[];
  results?: BulkActivityResult[];
};

type ResponseError = {
  response?: {
    status?: number;
    data?: ErrorResponseData;
    code?: unknown;
  };
  request?: unknown;
};

const isResponseError = (error: unknown): error is ResponseError => {
  return typeof error === "object" && error !== null;
};

export const getErrorMessageByCode = (code: ErrorCode) => {
  return errorMessages[code];
};

export const parseError = (error: unknown, message: string) => {
  if (!isResponseError(error)) {
    return "不明なエラーが発生しました";
  }

  if (error.response) {
    switch (error.response.status) {
      case 500:
        return message;
    }

    const code = error.response.data?.code ?? error.response.code;

    if (code && code === "VALIDATION_ERROR") {
      const validationErrorCode = error.response.data?.errors?.[0]?.code;
      if (isFieldErrorCode(validationErrorCode)) {
        return fieldErrorMessages[validationErrorCode];
      }
      return "不明なバリデーションエラーが発生しました";
    }
    if (!isErrorCode(code)) {
      return message;
    }

    return getErrorMessageByCode(code)
  };

  if (error.request) {
    return "リクエストがサーバーに到達できませんでした";
  };

  return "不明なエラーが発生しました";
};
