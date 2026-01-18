class PasswordMismatchError(Exception):
    """パスワード不一致エラー"""

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class EmailMismatchError(Exception):
    """メールアドレス不一致エラー"""

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class EmailAlreadyExistsError(Exception):
    """メールアドレス重複エラー"""

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)
