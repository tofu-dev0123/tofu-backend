from app.common.constant import Constant
from app.utils.format_utils import extension_formatter


class Message:
    LOGIN_SUCCESS = "ログインに成功しました"
    LOGOUT_SUCCESS = "ログアウトに成功しました"
    POST_CREATE_SUCCESS = "記事を作成しました"
    POST_UPDATE_SUCCESS = "記事を更新しました"
    POST_DELETE_SUCCESS = "記事を削除しました"
    IMAGE_DELETE_SUCCESS = "画像を削除しました"


class ErrorMessage:
    # バリデーションエラー
    # 認証関連
    VALIDATION_ERROR = "バリデーションエラーが発生しました"
    USERNAME_REQUIRED = "ユーザー名は必須項目です"
    USERNAME_MAX_LENGTH = (
        f"ユーザー名は{Constant.MAX_USERNAME_LENGTH}文字以内で入力してください"
    )
    USERNAME_FORMAT_EMAIL = "ユーザー名はメールアドレス形式で入力してください"
    PASSWORD_REQUIRED = "パスワードは必須項目です"
    PASSWORD_MIN_LENGTH = (
        f"パスワードは{Constant.MIN_PASSWORD_LENGTH}文字以上で入力してください"
    )
    PASSWORD_MAX_LENGTH = (
        f"パスワードは{Constant.MAX_PASSWORD_LENGTH}文字以内で入力してください"
    )

    # 記事関連
    TITLE_REQUIRED = "タイトルは必須項目です"
    TITLE_MAX_LENGTH = (
        f"タイトルは{Constant.MAX_TITLE_LENGTH}文字以内で入力してください"
    )
    CONTENT_MARKDOWN_REQUIRED = "マークダウン本文は必須項目です"
    CONTENT_MARKDOWN_SIZE_OVER = f"マークダウン本文のサイズは{(Constant.MAX_CONTENT_MARKDOWN_SIZE / (1024 * 1024))}MB以内で入力してください"
    CONTENT_HTML_REQUIRED = "HTML本文は必須項目です"
    THUMBNAIL_URL_MAX_LENGTH = (
        f"サムネイルURLは{Constant.MAX_THUMBNAIL_URL}文字以内で入力してください"
    )
    STATUS_REQUIRED = "公開ステータスは必須項目です"
    STATUS_ENUM = "公開ステータスは「DRAFT」,「PUBLISHED」で入力してください"
    IMAGES_ARRAY = "アップロード画像は配列で入力してください"
    IMAGES_VALUE = "アップロードIDは数値で入力してください"
    TAGS_ARRAY = "タグは配列で入力してください"
    TAGS_ARRAY_MAX_LENGTH = f"タグの個数は{Constant.MAX_TAGS}個以内にしてください"
    TAGS_MAX_LENGTH = f"タグは{Constant.MAX_TAG_LENGTH}文字以内で入力してください"
    KEYWORD_MAX_LENGTH = (
        f"キーワードは{Constant.MAX_KEYWORD_LENGTH}文字以内で入力してください"
    )
    MIN_OFFSET = f"オフセット値は{Constant.MIN_OFFSET}以上の整数で指定してください"
    MIN_LIMIT = f"リミット値は{Constant.MIN_LIMIT}以上の整数で指定してください"
    MAX_LIMIT = f"リミット値は{Constant.MAX_LIMIT}以下の整数で指定してください"
    POST_ID_REQUIRED = "記事IDは必須項目です"
    MIN_POST_ID = f"記事IDは{Constant.MIN_POST_ID}以上の整数で指定してください"

    # 画像関連
    MAX_FILE_SIZE = f"アップロードできる画像ファイルは{Constant.MAX_FILE_SIZE / (1024 * 1024)}MBまでです"
    ALLOWED_EXTENSIONS = f"アップロードできる画像ファイルの拡張子は{extension_formatter(Constant.ALLOWED_EXTENSIONS)}です"
    MAX_ALT_TEXT_LENGTH = (
        f"代替テキストは{Constant.MAX_ALT_TEXT_LENGTH}文字以内で入力してください"
    )
    IMAGE_ID_REQUIRED = "画像IDは必須項目です"
    MIN_IMAGE_ID = f"画像IDは{Constant.MIN_IMAGE_ID}以上の整数で指定してください"
    INVALID_IMAGE_OWNER = "削除対象の画像ID（{image_id}）がこの記事に紐づいていません"

    # 認証エラー
    TOKEN_REQUIRED = "認証トークンが必要です"
    AUTHENTICATION_ERROR = "認証に失敗しました"
    LOGIN_FAIL = "ユーザー名またはパスワードが間違っています"

    # 記事関連
    IMAGE_NOT_EXIST = "指定した画像IDが存在しません"
    NOT_EXIST = "指定した記事が存在しません"
    NOT_EXIST_ON_STORAGE = "ストレージに対象ファイルが存在しません"
    BAD_REQUEST_OF_THUMBNAIL = "新規サムネイルを登録する場合は削除フラグはOFFにしてください"

    # s3関連
    S3_FILE_UPLOAD_ERROR = "s3へのファイルアップロードに失敗しました"
    S3_FILE_DELETE_ERROR = "s3のファイル削除に失敗しました"

    # INTERNAL_SERVER_ERROR関連
    INTERNAL_SERVER_ERROR = "サーバーエラーが発生しました"
