class Message:
    LOGIN_SUCCESS = "ログインに成功しました"
    LOGOUT_SUCCESS = "ログアウトに成功しました"
    POST_CREATE_SUCCESS = "記事を作成しました"


class ErrorMessage:
    # バリデーションエラー
    # 認証関連
    VALIDATION_ERROR = "バリデーションエラーが発生しました"
    USERNAME_REQUIRED = "ユーザー名は必須項目です"
    USERNAME_MAX_LENGTH = "ユーザー名は50文字以内で入力してください"
    USERNAME_FORMAT_EMAIL = "ユーザー名はメールアドレス形式で入力してください"
    PASSWORD_REQUIRED = "パスワードは必須項目です"
    PASSWORD_MIN_LENGTH = "パスワードは8文字以上で入力してください"
    PASSWORD_MAX_LENGTH = "パスワードは50文字以内で入力してください"

    # 記事関連
    TITLE_REQUIRED = "タイトルは必須項目です"
    TITLE_MAX_LENGTH = "タイトルは255文字以内で入力してください"
    CONTENT_MARKDOWN_REQUIRED = "マークダウン本文は必須項目です"
    CONTENT_MARKDOWN_SIZE_OVER = "マークダウン本文のサイズは1MB以内で入力してください"
    CONTENT_HTML_REQUIRED = "HTML本文は必須項目です"
    THUMBNAIL_URL_MAX_LENGTH = "サムネイルURLは500文字以内で入力してください"
    STATUS_REQUIRED = "公開ステータスは必須項目です"
    STATUS_ENUM = "公開ステータスは「DRAFT」,「PUBLISHED」で入力してください"
    IMAGES_ARRAY = "アップロード画像は配列で入力してください"
    IMAGES_VALUE = "アップロードIDは数値で入力してください"
    TAGS_ARRAY = "タグは配列で入力してください"
    TAGS_ARRAY_MAX_LENGTH = "タグの個数は20個以内にしてください"
    TAGS_MAX_LENGTH = "タグは30文字以内で入力してください"

    # 認証エラー
    TOKEN_REQUIRED = "認証トークンが必要です"
    AUTHENTICATION_ERROR = "認証に失敗しました"
    LOGIN_FAIL = "ユーザー名またはパスワードが間違っています"

    # 記事関連
    IMAGE_NOT_EXIST = "指定した画像IDが存在しません"

    # INTERNAL_SERVER_ERROR関連
    INTERNAL_SERVER_ERROR = "サーバーエラーが発生しました"
