from fastapi import APIRouter, Depends, UploadFile, File, Form, Path
from app.common.message import Message
from app.api.deps import get_image_service
from app.core.security import get_current_user
from app.schemas.image import ImageUploadResponse, ImageDeleteResponse
from app.services.image_service import ImageService
from app.models.user import User
from app.common.constant import Constant

router = APIRouter(prefix="/images", tags=["Image 画像関連"])


@router.post("/upload", response_model=ImageUploadResponse)
async def upload(
    image_file: UploadFile = File(...),
    alt_text: str | None = Form(None),
    service: ImageService = Depends(get_image_service),
    current_user: User = Depends(get_current_user),
) -> ImageUploadResponse:
    service.validate(image_file, alt_text)

    result = service.upload_file(image_file, alt_text)

    return result


@router.delete("/{image_id}", response_model=ImageDeleteResponse)
async def delete(
    image_id: int = Path(..., ge=Constant.MIN_IMAGE_ID, description="画像ID"),
    service: ImageService = Depends(get_image_service),
    current_user: User = Depends(get_current_user),
) -> ImageDeleteResponse:
    service.delete_image(image_id)

    return ImageDeleteResponse(message=Message.IMAGE_DELETE_SUCCESS)
