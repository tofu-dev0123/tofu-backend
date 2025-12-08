from typing import List
from app.core.exceptions.post_exceptions import ImageNotExistError

def check_image_list(images: List[int]):
    if len(images) == 0:
        raise ImageNotExistError(message="エラーです")