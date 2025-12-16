from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List
from app.core.exceptions.image_exceptions import ImageUploadValidationError
from app.repositories.image_repository import ImageRepository
from app.common.constant import Constant
from app.common.message import ErrorMessage


class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.image_repo = ImageRepository(db)
    
    
    async def validate(self, image_file: UploadFile, alt_text: str | None):
        VALUE = "image_file"
        errors = []
        
        # ファイルサイズチェック
        content = await image_file.read()
        if len(content) > Constant.MAX_FILE_SIZE:
            errors.append({"value": VALUE, "message":ErrorMessage.MAX_FILE_SIZE})
        
        # 拡張子チェック
        extension = image_file.filename.split(".")[-1].lower()
        if extension not in Constant.ALLOWED_EXTENSIONS:
            errors.append({"value": VALUE, "message":ErrorMessage.ALLOWED_EXTENSIONS})
        
        # 代替テキストサイズチェック
        if alt_text and len(alt_text) > Constant.MAX_ALT_TEXT_LENGTH:
            errors.append({"value": VALUE, "message":ErrorMessage.MAX_ALT_TEXT_LENGTH})
            
        if errors:
            raise ImageUploadValidationError(errors)
