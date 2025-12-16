from fastapi import APIRouter, Depends, UploadFile, File, Form
import logging
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.schemas.image import ImageUploadResponse
from app.services.image_service import ImageService
from app.models.user import User

router = APIRouter(prefix="/images", tags=["Image 画像関連"])
logger = logging.getLogger(__name__)


def get_image_service(
    db: Session = Depends(get_db),
) -> ImageService:
    return ImageService(db)


@router.post("/upload", response_model=ImageUploadResponse)
async def upload(
    image_file: UploadFile = File(...),
    alt_text: str | None = Form(None),
    service: ImageService = Depends(get_image_service),
    current_user: User = Depends(get_current_user),
):
    try:
        service.validate(image_file, alt_text)

        result = service.upload_file(image_file, alt_text)

    except Exception as e:
        logger.error(e.response)
        raise

    return result
