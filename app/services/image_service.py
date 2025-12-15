from sqlalchemy.orm import Session
from pydantic_core import PydanticCustomError
from fastapi import UploadFile
from app.repositories.image_repository import ImageRepository
from app.common.constant import Constant


class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.image_repo = ImageRepository(db)
    
    
    async def validate(self, image_file: UploadFile, alt_text: str | None):
        errors = []
        
        if not image_file:
            errors.append(("missing", ""))
        
        content = await image_file.read()
        if content.size > Constant.MAX_FILE_SIZE:
            errors.append(("size_over", ""))
        image_file.file.seek(0)
        
        extension = image_file.filename.split(".")[-1].lower()
        if extension not in Constant.ALLOWED_EXTENSIONS:
            errors.append(("not_allowed", ""))
        
        if alt_text and len(alt_text) > 255:
            errors.append(("string_too_long", ""))
            
        if errors:
            raise PydanticCustomError(errors)
