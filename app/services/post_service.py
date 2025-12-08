from sqlalchemy.orm import Session
from typing import List
from app.repositories.image_repository import find_by_image_id
from app.core.exceptions.post_exceptions import ImageNotExistError


def check_image_list(images: List[int], db: Session):
    for id in images:
        image_data = find_by_image_id(db, id)

        if image_data is None:
            raise ImageNotExistError(message="")
