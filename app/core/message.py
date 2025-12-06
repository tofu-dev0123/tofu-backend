class Message:
  LOGIN_SUCCESS = "ログインに成功しました"

class ErrorMessage:
  # バリデーションエラー関連
  VALIDATION_ERROR = "バリデーションエラーが発生しました"
  USERNAME_REQUIRED = "ユーザー名は必須項目です"
  PASSWORD_REQUIRED = "パスワードは必須項目です"
  USERNAME_MAX_LENGTH = "ユーザー名は50文字以内で入力してください"
  USERNAME_FORMAT_EMAIL = "ユーザー名はメールアドレス形式で入力してください"
  PASSWORD_MIN_LENGTH = "パスワードは8文字以上で入力してください"
  PASSWORD_MAX_LENGTH = "パスワードは50文字以内で入力してください"
  
  # ログイン関連
  LOGIN_FAIL = "ユーザー名またはパスワードが間違っています"

  # INTERNAL_SERVER_ERROR関連
  INTERNAL_SERVER_ERROR = "サーバーエラーが発生しました"