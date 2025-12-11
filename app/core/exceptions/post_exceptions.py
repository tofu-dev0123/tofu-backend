class ImageNotExistError(Exception):
    """画像IDが存在しないエラー"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
