from app.common.constant import Constant
from app.utils.format_utils import extension_formatter


class Message:
    LOGIN_SUCCESS = "ログインに成功しました"
    LOGOUT_SUCCESS = "ログアウトに成功しました"
    POST_CREATE_SUCCESS = "記事を作成しました"
    POST_UPDATE_SUCCESS = "記事を更新しました"
    POST_DELETE_SUCCESS = "記事を削除しました"
    POST_PATCH_SUCCESS = "公開ステータスを{status}に更新しました"
    IMAGE_DELETE_SUCCESS = "画像を削除しました"
    ACCOUNT_UPDATE_SUCCESS = "アカウント情報を更新しました"
    PASSWORD_CHANGE_SUCCESS = "パスワードを変更しました"
    EMAIL_CHANGE_SUCCESS = "メールアドレスを変更しました"
    PROFILE_UPDATE_SUCCESS = "プロフィールを更新しました"
    TIMELINE_CREATE_SUCCESS = "年表を作成しました"
    TIMELINE_UPDATE_SUCCESS = "年表を更新しました"
    TIMELINE_DELETE_SUCCESS = "年表を削除しました"
    PRODUCT_CREATE_SUCCESS = "プロダクトを作成しました"
    PRODUCT_UPDATE_SUCCESS = "プロダクトを更新しました"
    PRODUCT_DELETE_SUCCESS = "プロダクトを削除しました"


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
    TITLE_REQUIRED_FOR_PUBLISHED = "公開時はタイトルは必須項目です"
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

    # プロフィール関連
    HEADLINE_REQUIRED = "肩書きは必須項目です"
    HEADLINE_MAX_LENGTH = (
        f"肩書きは{Constant.MAX_HEADLINE_LENGTH}文字以内で入力してください"
    )
    BIO_REQUIRED = "自己紹介文は必須項目です"
    BIO_MAX_LENGTH = f"自己紹介文は{Constant.MAX_BIO_LENGTH}文字以内で入力してください"
    SITE_DESCRIPTION_REQUIRED = "サイト説明文は必須項目です"
    SITE_DESCRIPTION_MAX_LENGTH = (
        f"サイト説明文は{Constant.MAX_SITE_DESCRIPTION_LENGTH}文字以内で入力してください"
    )

    # 年表関連
    YEAR_REQUIRED = "年は必須項目です"
    YEAR_TYPE = "年は数値で入力してください"
    YEAR_RANGE = (
        f"年は{Constant.MIN_YEAR}〜{Constant.MAX_YEAR}の範囲で入力してください"
    )
    TIMELINE_TITLE_MAX_LENGTH = (
        f"見出しは{Constant.MAX_TIMELINE_TITLE_LENGTH}文字以内で入力してください"
    )
    TIMELINE_BODY_MAX_LENGTH = (
        f"本文は{Constant.MAX_TIMELINE_BODY_LENGTH}文字以内で入力してください"
    )
    TIMELINE_ID_REQUIRED = "年表IDは必須項目です"
    MIN_TIMELINE_ID = f"年表IDは{Constant.MIN_TIMELINE_ID}以上の整数で指定してください"

    # プロダクト関連
    PRODUCT_TITLE_REQUIRED = "タイトルは必須項目です"
    PRODUCT_TITLE_MAX_LENGTH = (
        f"タイトルは{Constant.MAX_PRODUCT_TITLE_LENGTH}文字以内で入力してください"
    )
    PRODUCT_DESCRIPTION_MAX_LENGTH = (
        f"説明は{Constant.MAX_PRODUCT_DESCRIPTION_LENGTH}文字以内で入力してください"
    )
    LINK_URL_MAX_LENGTH = (
        f"リンクURLは{Constant.MAX_LINK_URL_LENGTH}文字以内で入力してください"
    )
    PRODUCT_ID_REQUIRED = "プロダクトIDは必須項目です"
    MIN_PRODUCT_ID = f"プロダクトIDは{Constant.MIN_PRODUCT_ID}以上の整数で指定してください"

    # 表示順（年表・プロダクト共通）
    SORT_ORDER_MIN = (
        f"表示順は{Constant.MIN_SORT_ORDER}以上の整数で指定してください"
    )
    MIN_OFFSET = f"オフセット値は{Constant.MIN_OFFSET}以上の整数で指定してください"
    MIN_LIMIT = f"リミット値は{Constant.MIN_LIMIT}以上の整数で指定してください"
    MAX_LIMIT = f"リミット値は{Constant.MAX_LIMIT}以下の整数で指定してください"
    POST_ID_REQUIRED = "記事IDは必須項目です"
    MIN_POST_ID = f"記事IDは{Constant.MIN_POST_ID}以上の整数で指定してください"
    MIN_PAGE = f"ページは{Constant.MIN_PAGE}以上の整数で指定してください"

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
    TIMELINE_NOT_EXIST = "指定した年表が存在しません"
    PRODUCT_NOT_EXIST = "指定したプロダクトが存在しません"
    PROFILE_NOT_EXIST = "プロフィールが存在しません"
    NOT_EXIST_ON_STORAGE = "ストレージに対象ファイルが存在しません"
    BAD_REQUEST_OF_THUMBNAIL = (
        "新規サムネイルを登録する場合は削除フラグはOFFにしてください"
    )

    # s3関連
    S3_FILE_UPLOAD_ERROR = "s3へのファイルアップロードに失敗しました"
    S3_FILE_DELETE_ERROR = "s3のファイル削除に失敗しました"

    # INTERNAL_SERVER_ERROR関連
    INTERNAL_SERVER_ERROR = "サーバーエラーが発生しました"

    # アカウント関連
    PASSWORD_MISMATCH = "現在のパスワードが正しくありません"
    EMAIL_MISMATCH = "現在のメールアドレスが正しくありません"
    EMAIL_ALREADY_EXISTS = "このメールアドレスは既に使用されています"
    ACCOUNT_NAME_REQUIRED = "アカウント名は必須項目です"
    ACCOUNT_NAME_MAX_LENGTH = (
        f"アカウント名は{Constant.MAX_ACCOUNT_NAME_LENGTH}文字以内で入力してください"
    )
    ACCOUNT_NAME_BLANK = "アカウント名は空白のみは不可です"
    NEW_PASSWORD_SAME = (
        "新しいパスワードは現在のパスワードと異なるものを設定してください"
    )
    NEW_EMAIL_SAME = (
        "新しいメールアドレスは現在のメールアドレスと異なるものを設定してください"
    )
