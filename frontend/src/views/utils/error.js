export const parseLoginError = (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 422:
        return error.response.data.detail
      case 500:
        return "ログインに失敗しました"
      default:
        return error.response.data.detail
    }
  }

  if (error.request) {
    return "リクエストがサーバーに到達できませんでした"
  }

  return "不明なエラーが発生しました"
}
