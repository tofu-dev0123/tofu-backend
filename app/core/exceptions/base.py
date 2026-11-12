class BaseAppError(Exception):
    """message 属性を持つアプリケーション例外の基底クラス"""

    default_message: str = ""

    def __init__(self, message: str | None = None) -> None:
        self.message: str = self.default_message if message is None else message
        super().__init__(self.message)
