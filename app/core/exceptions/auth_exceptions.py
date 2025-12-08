class LoginFailError(Exception):
    """ログイン失敗エラー"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """認証エラー"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)